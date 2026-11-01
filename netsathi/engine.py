"""Deterministic rules. Every diagnosis lists the evidence that made its rule fire."""
from .models import Status, Diagnosis
from . import plain

LIMITS = ["A test message with no reply can be caused by a firewall or router that ignores it.",
          "These results describe this moment only. They don't prove every website works."]

def diagnose(results, simulated=False) -> Diagnosis:
    r = {c.id: c for c in results}
    s = lambda k: r[k].status if k in r else Status.SKIPPED
    ev = lambda *ids: [f"{plain.line(r[i])} ({r[i].observed})" for i in ids if i in r]
    local, gw, ext, dns, alt = s("local"), s("gateway"), s("external"), s("dns"), s("dns_alt")
    facts = [f"{plain.title(c)}: {c.status.value}. {c.observed}" for c in results]
    mk = lambda **k: Diagnosis(facts=facts, limitations=LIMITS, simulated=simulated, **k)
    P, F = Status.PASS, Status.FAIL

    if ext == P and dns == P:
        return mk(key="ok", title="The tests worked this time", certainty="no problem observed",
            found="Your computer reached a known internet address and found a website's address.",
            meaning="Your connection worked at the moment of the test. That doesn't prove every website works, or that a problem that comes and goes is gone.",
            why=ev("external", "dns"), verify="If the problem comes back, run NetSathi again while it is happening.")
    if ext == P and dns == F:
        causes = ["The address book service (DNS) your computer uses may not be answering."]
        if alt == P: causes.append("A separate public service did answer, which points at the service your computer normally uses, not at your internet link.")
        if alt == F: causes.append("The public service didn't answer either, so this network may block address lookups.")
        return mk(key="dns", title="Your computer couldn't find the website address (DNS)", certainty="likely",
            found="Your computer reached an internet address by number, but could not look up the address for a website name.",
            meaning="Websites may fail to load even though the internet link itself seems to work. DNS is like an address book that helps your computer find websites.",
            why=ev("external", "dns", "dns_alt"), causes=causes,
            verify="After the steps, press Retest. The lookup should show as worked.")
    if local in (F, Status.WARNING) or gw == F:
        return mk(key="local", title="Your computer's own connection setup may have a problem", certainty="possible",
            found="Your computer doesn't seem to have a complete connection setup, such as an address or a device to send traffic through.",
            meaning="Your computer may not be properly joined to the network. This does not mean your router is broken.",
            why=ev("local", "gateway", "routing"), causes=["The Wi-Fi or cable connection may have dropped, or the network didn't give your computer an address."],
            verify="After the steps, press Retest. Your connection setup should show as worked.")
    if local == P and gw == Status.INCONCLUSIVE and ext == F and dns != P:
        return mk(key="gateway_silent", title="Your router didn't answer, and the internet test failed", certainty="possible",
            found="Your computer has an address, but the router didn't answer the test and no internet address replied.",
            meaning="Many routers ignore this test, so silence doesn't prove the router is broken. We need one more check before blaming anything.",
            why=ev("local", "gateway", "external"), causes=["The router may be off, or it may ignore tests.", "Your internet provider may have a problem.", "A firewall may block these tests."],
            verify="After the steps, press Retest. The internet test should show as worked.")
    if ext == F and dns == F and local == P:
        return mk(key="upstream", title="We couldn't confirm any connection to the internet", certainty="possible",
            found="Your computer has an address, but neither the internet test nor the website lookup worked.",
            meaning="The problem may be outside your computer, for example at your router or internet provider, or a filter may be blocking the tests.",
            why=ev("local", "gateway", "external", "dns"), causes=["Your router or internet provider may have an outage.", "A filter or firewall may block these tests."],
            verify="After the steps, press Retest. At least the internet test should show as worked.")
    missing = [plain.title(c) for c in results if c.status in (Status.INCONCLUSIVE, Status.SKIPPED, Status.ERROR)]
    return mk(key="inconclusive", title="NetSathi couldn't tell what is wrong", certainty="inconclusive",
        found="The tests gave mixed answers, or some tests couldn't run.",
        meaning="We can't name a cause confidently, so we won't guess." + (" Unclear tests: " + "; ".join(missing) + "." if missing else ""),
        why=ev(*[c.id for c in results]), verify="Press Retest once. If it is still unclear, try the steps and tell your network administrator what NetSathi showed.")

def compare(before, after) -> str:
    b = {c.id: c.status for c in before}; a = {c.id: c.status for c in after}
    bad = {Status.FAIL, Status.WARNING}
    fixed = [k for k in a if b.get(k) in bad and a[k] == Status.PASS]
    still = [k for k in a if b.get(k) in bad and a[k] in bad]
    worse = [k for k in a if b.get(k) == Status.PASS and a[k] in bad]
    if fixed and not still and not worse: return "The problem appears resolved in this test."
    if still and not fixed: return "The problem is still there."
    if fixed or worse: return "Results are mixed."
    return "Inconclusive: nothing measurable changed."
