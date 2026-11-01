import pathlib
from streamlit.testing.v1 import AppTest
APP = str(pathlib.Path(__file__).parent.parent / "app.py")
def btn(at, label): return [b for b in at.button if b.label == label][0]
def demo(at):
    at.sidebar.radio(key="mode_sel").set_value("Demo Mode").run(); return at
def test_demo_journey_with_cant_find_and_report():
    at = demo(AppTest.from_file(APP, default_timeout=30).run()); assert not at.exception
    at.radio(key="symptom").set_value("Websites won't load").run()
    btn(at, "Start diagnosis").click().run(); assert any("Demo mode" in m.value for m in at.markdown)
    btn(at, "See what we found").click().run(); assert "address" in at.title[0].value and not at.exception
    assert [h.value for h in at.header][:3] == ["1. What we found", "2. What this means for you", "3. Why we think this"]
    btn(at, "Open the step-by-step guide").click().run()
    assert btn(at, "Continue").disabled
    at.radio(key="ans_dns_0").set_value("I can't find this setting").run()
    assert any("Try this instead" in i.value for i in at.info) and not btn(at, "Continue").disabled
    btn(at, "Continue").click().run(); assert any("Step 2 of 5" in str(p.proto) for p in at.get("progress"))
def test_symptom_reaches_report_and_retest_compares():
    at = demo(AppTest.from_file(APP, default_timeout=30).run())
    at.radio(key="symptom").set_value("Websites won't load").run()
    btn(at, "Start diagnosis").click().run(); at.sidebar.checkbox(key="demo_fixed").set_value(True).run()
    at.sidebar.radio(key="view").set_value("Results").run(); btn(at, "Retest now").click().run()
    assert any("resolved" in i.value for i in at.info), [i.value for i in at.info]
def test_switching_mode_clears_session():
    at = demo(AppTest.from_file(APP, default_timeout=30).run()); btn(at, "Start diagnosis").click().run()
    at.sidebar.radio(key="mode_sel").set_value("Live Diagnosis").run(); assert at.session_state["results"] is None
def test_live_mode_runs_without_crashing():
    at = AppTest.from_file(APP, default_timeout=90).run(); btn(at, "Start diagnosis").click().run(); assert not at.exception
