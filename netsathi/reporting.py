import json, platform, uuid
from dataclasses import asdict
from datetime import datetime, timezone
from . import plain
from .guidance import flow_for

def build_report(symptom, results, dx, retest_note=None, guide_log=None) -> str:
    sim = any(c.simulated for c in results)
    unresolved = [plain.title(c) for c in results if c.status.value in ("INCONCLUSIVE", "SKIPPED", "ERROR")]
    rep = {
     "report_id": uuid.uuid4().hex[:12], "timestamp": datetime.now(timezone.utc).isoformat(),
     "results_are": "SIMULATED (demo mode, not measured)" if sim else "REAL (measured on this computer)",
     "summary": {"selected_problem": symptom or "not recorded", "what_we_found": dx.found, "what_it_means": dx.meaning,
                 "certainty": dx.certainty, "possible_causes": dx.causes, "evidence": dx.why,
                 "recommended_actions": [st["title"] for st in flow_for(dx)[2]], "how_to_check": dx.verify,
                 "retest_result": retest_note or "No retest yet", "unresolved": unresolved or "None",
                 "steps_you_reported": guide_log or []},
     "limitations": dx.limitations,
     "checks": [{"name": plain.title(c), "technical_name": plain.tech(c), "result": c.status.value, "what_was_observed": c.observed,
                 "what_this_test_can_and_cannot_show": plain.limits(c)} for c in results],
     "technical_details": {"operating_system": platform.system(), "checks_raw": [{**asdict(c), "status": c.status.value} for c in results]},
    }
    return json.dumps(rep, indent=2, default=str)
