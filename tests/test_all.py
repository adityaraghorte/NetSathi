import json, socket
from netsathi import diagnostics as d
from netsathi.engine import diagnose, compare
from netsathi.demo import SCENARIOS
from netsathi.models import Status, CheckResult
from netsathi.reporting import build_report

def test_dns_scenario(): assert diagnose(SCENARIOS["DNS failure"]).key == "dns"
def test_local_scenario(): assert diagnose(SCENARIOS["Local configuration problem"]).key == "local"
def test_ok_scenario(): assert diagnose(SCENARIOS["Everything works"]).certainty == "no problem observed"
def test_inconclusive(): assert diagnose(SCENARIOS["Inconclusive"]).certainty == "inconclusive"
def test_gateway_ping_failure_alone_not_definitive(monkeypatch):
    monkeypatch.setattr(d, "find_gateway", lambda: "192.168.1.1"); monkeypatch.setattr(d, "ping", lambda h, t=3: "no_reply")
    assert d.check_gateway().status == Status.INCONCLUSIVE
def test_missing_gateway(monkeypatch):
    monkeypatch.setattr(d, "find_gateway", lambda: None); assert d.check_gateway().status == Status.FAIL
def test_ping_utility_missing(monkeypatch):
    def boom(*a, **k): raise FileNotFoundError
    monkeypatch.setattr(d, "_run", boom); assert d.ping("1.1.1.1") == "unavailable"
def test_dns_fail(monkeypatch):
    def boom(*a, **k): raise socket.gaierror
    monkeypatch.setattr(socket, "getaddrinfo", boom); assert d.check_dns().status == Status.FAIL
def test_dns_ok(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("1.2.3.4", 0))]); assert d.check_dns().status == Status.PASS
def test_retest_resolved():
    assert "resolved" in compare(SCENARIOS["DNS failure"], SCENARIOS["Everything works"])
def test_report_flags_simulation():
    rep = json.loads(build_report("x", SCENARIOS["DNS failure"], diagnose(SCENARIOS["DNS failure"], True)))
    assert "SIMULATED" in rep["results_are"] and len(rep["checks"]) == 4

import time
def test_timeout_reported_not_hung(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: time.sleep(0.6))
    r = d.check_dns(timeout_s=0.1); assert r.status == Status.FAIL and "timed out" in r.observed
def test_routing_skipped_when_utility_missing(monkeypatch):
    def boom(*a, **k): raise FileNotFoundError
    monkeypatch.setattr(d, "_run", boom); assert d.check_routing().status == Status.SKIPPED
def test_alt_resolver_failure(monkeypatch):
    def boom(*a, **k): raise OSError
    monkeypatch.setattr(d, "_dns_query", boom); assert d.check_dns_alt().status == Status.FAIL
def test_dns_cause_mentions_public_resolver():
    rs = list(SCENARIOS["DNS failure"]) + [CheckResult("dns_alt", "x", Status.PASS, "ok")]
    assert any("public service" in c for c in diagnose(rs).causes)
def test_conflicting_evidence_inconclusive():
    rs = [CheckResult("local","l",Status.PASS,""), CheckResult("external","e",Status.FAIL,""), CheckResult("dns","d",Status.PASS,"")]
    assert diagnose(rs).certainty == "inconclusive"
def test_missing_checks_dont_overstate():
    assert diagnose([]).certainty == "inconclusive"
def test_simulated_flag_isolated():
    assert all(c.simulated for c in SCENARIOS["Everything works"]) and not d.check_local().simulated
def test_retest_persists():
    assert compare(SCENARIOS["DNS failure"], SCENARIOS["DNS failure"]) == "The problem is still there."
def test_guidance_exists_for_every_scenario():
    from netsathi.guidance import steps_for
    for s in SCENARIOS.values(): assert steps_for(diagnose(s))

from netsathi.guidance import FLOWS, flow_for
from netsathi import explain
def test_every_flow_has_complete_steps_and_ends_with_retest():
    for k, (t, why, steps) in FLOWS.items():
        assert t and why and steps[-1]["retest"]
        for st_ in steps:
            for f in ("purpose", "look_for", "if_ok", "if_not", "alt"): assert st_[f]
            assert st_["how"]["11"] and st_["how"]["10"]
def test_every_diagnosis_has_a_flow_and_evidence():
    for sc in SCENARIOS.values():
        dx = diagnose(sc); assert flow_for(dx) and dx.why and dx.verify
def test_gateway_silence_not_called_broken():
    rs = [CheckResult("local","l",Status.PASS,"ip"), CheckResult("gateway","g",Status.INCONCLUSIVE,"no_reply"), CheckResult("external","e",Status.FAIL,"x"), CheckResult("dns","d",Status.FAIL,"x")]
    dx = diagnose(rs); assert dx.key == "gateway_silent" and "broken" in dx.meaning and "doesn't prove" in dx.meaning
def test_empty_results_have_recovery_flow():
    assert flow_for(diagnose([])).__len__() == 3
def test_report_plain_and_no_secrets(monkeypatch):
    monkeypatch.setenv("OLLAMA_API_KEY", "sk-secret")
    dx = diagnose(SCENARIOS["DNS failure"], True); out = build_report("Websites won't load", SCENARIOS["DNS failure"], dx, "still there", ["a: b"])
    assert "sk-secret" not in out and "SIMULATED" in out and "Websites won't load" in out
    j = json.loads(out); assert j["summary"]["recommended_actions"] and j["summary"]["retest_result"] == "still there"
