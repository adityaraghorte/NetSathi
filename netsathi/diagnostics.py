"""Real, bounded, read-only checks. No shell strings, no system changes."""
import platform, re, socket, subprocess, time, concurrent.futures as cf
from .models import CheckResult, Status

EXTERNAL_TARGETS = ("1.1.1.1", "8.8.8.8")
DNS_HOST = "example.com"

def _run(args, timeout=6):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)

def _timed(fn):
    t = time.perf_counter(); r = fn(); r.duration_s = round(time.perf_counter() - t, 3); return r

def check_local() -> CheckResult:
    def go():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2); s.connect(("192.0.2.1", 9))  # UDP connect sends no packet
            ip = s.getsockname()[0]; s.close()
        except OSError as e:
            return CheckResult("local", "Local IP configuration", Status.FAIL,
                               f"No usable outbound IPv4 address ({e.__class__.__name__})",
                               "The computer has no route to select a local address.")
        if ip.startswith("169.254."):
            return CheckResult("local", "Local IP configuration", Status.WARNING, f"Link-local address {ip}",
                               "Address looks self-assigned (DHCP may have failed).")
        return CheckResult("local", "Local IP configuration", Status.PASS, f"Local IPv4 {ip}",
                           "An address was selected for outbound traffic.")
    return _timed(go)

def find_gateway():
    try:
        if platform.system() == "Windows":
            out = _run(["ipconfig"]).stdout
            m = re.search(r"Default Gateway[ .]*:\s*(\d+\.\d+\.\d+\.\d+)", out)
        else:
            out = _run(["ip", "route", "show", "default"]).stdout
            m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", out)
        return m.group(1) if m else None
    except (OSError, subprocess.SubprocessError):
        return "UNAVAILABLE"

def ping(host, timeout_s=3) -> str:
    """Returns 'ok', 'no_reply', or 'unavailable'."""
    flag = ["-n", "1", "-w", str(timeout_s * 1000)] if platform.system() == "Windows" else ["-c", "1", "-W", str(timeout_s)]
    try:
        return "ok" if _run(["ping", *flag, host], timeout_s + 3).returncode == 0 else "no_reply"
    except (OSError, subprocess.SubprocessError):
        return "unavailable"

def check_gateway() -> CheckResult:
    def go():
        gw = find_gateway()
        if gw == "UNAVAILABLE":
            return CheckResult("gateway", "Default gateway", Status.INCONCLUSIVE, "Could not read routing info", "Needed utility unavailable.")
        if gw is None:
            return CheckResult("gateway", "Default gateway", Status.FAIL, "No default gateway configured", "No route toward other networks.")
        p = ping(gw)
        st = {"ok": Status.PASS, "no_reply": Status.INCONCLUSIVE, "unavailable": Status.INCONCLUSIVE}[p]
        note = "Gateway replied." if p == "ok" else "No ping reply; routers often block ICMP, so this does not prove the gateway is down."
        return CheckResult("gateway", "Default gateway", st, f"Gateway {gw}: ping {p}", note)
    return _timed(go)

def check_external(targets=EXTERNAL_TARGETS) -> CheckResult:
    def go():
        res = {t: ping(t) for t in targets}
        obs = ", ".join(f"{t}: {v}" for t, v in res.items())
        vals = set(res.values())
        if "ok" in vals:
            return CheckResult("external", "External IP reachability", Status.PASS, obs, "At least one external IP replied to ping.")
        if vals == {"unavailable"}:
            return CheckResult("external", "External IP reachability", Status.INCONCLUSIVE, obs, "ping utility unavailable.")
        return CheckResult("external", "External IP reachability", Status.FAIL, obs, "No external target replied (ICMP may be blocked).")
    return _timed(go)

def check_dns(host=DNS_HOST, timeout_s=5) -> CheckResult:
    def go():
        ex = cf.ThreadPoolExecutor(max_workers=1)
        fut = ex.submit(socket.getaddrinfo, host, None, socket.AF_INET)
        try:
            addr = fut.result(timeout=timeout_s)[0][4][0]
            return CheckResult("dns", "DNS resolution", Status.PASS, f"{host} -> {addr}", "System resolver answered.")
        except cf.TimeoutError:
            return CheckResult("dns", "DNS resolution", Status.FAIL, f"{host}: timed out after {timeout_s}s", "Resolver did not answer in time.")
        except OSError as e:
            return CheckResult("dns", "DNS resolution", Status.FAIL, f"{host}: {e.__class__.__name__}", "System resolver could not resolve the name.")
        finally:
            ex.shutdown(wait=False)
    return _timed(go)


def check_routing() -> CheckResult:
    """Read-only routing table summary (no traceroute)."""
    def go():
        args = ["route", "print", "-4"] if platform.system() == "Windows" else ["ip", "route"]
        try:
            out = _run(args).stdout
        except (OSError, subprocess.SubprocessError):
            return CheckResult("routing", "Routing table", Status.SKIPPED, f"'{args[0]}' unavailable", "Routing info could not be read on this system.")
        n = len([l for l in out.splitlines() if re.match(r"\s*(\d+\.\d+\.\d+\.\d+|default)", l)])
        d = len(re.findall(r"^\s*(?:0\.0\.0\.0\s+0\.0\.0\.0|default)", out, re.M))
        st = Status.PASS if d else Status.WARNING
        return CheckResult("routing", "Routing table", st, f"{n} routes, {d} default route(s)", "Read-only summary of the routing table.")
    return _timed(go)

def _dns_query(host, server, timeout_s):
    import struct, os
    qid = os.urandom(2)
    q = qid + struct.pack(">HHHHH", 0x0100, 1, 0, 0, 0) + b"".join(bytes([len(p)]) + p.encode() for p in host.split(".")) + b"\x00" + struct.pack(">HH", 1, 1)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(timeout_s)
    try:
        s.sendto(q, (server, 53)); data = s.recv(512)
    finally:
        s.close()
    return data[:2] == qid and (data[3] & 0x0F) == 0 and struct.unpack(">H", data[6:8])[0] > 0

def check_dns_alt(host=DNS_HOST, server="1.1.1.1", timeout_s=3) -> CheckResult:
    """Limited test: one UDP DNS query straight to a public resolver. Shows whether that resolver is reachable, nothing more."""
    def go():
        try:
            ok = _dns_query(host, server, timeout_s)
        except OSError as e:
            return CheckResult("dns_alt", "Public resolver test", Status.FAIL, f"{server}: {e.__class__.__name__}", "No DNS reply (port 53 may be filtered).")
        if ok: return CheckResult("dns_alt", "Public resolver test", Status.PASS, f"{server} answered for {host}", "A separate resolver answered.")
        return CheckResult("dns_alt", "Public resolver test", Status.INCONCLUSIVE, f"{server}: unexpected reply", "Reply was empty or malformed.")
    return _timed(go)

ALL_CHECKS = [check_local, check_gateway, check_routing, check_external, check_dns, check_dns_alt]
