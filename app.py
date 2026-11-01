import streamlit as st
from netsathi.diagnostics import ALL_CHECKS
from netsathi.engine import diagnose, compare
from netsathi.demo import SCENARIOS
from netsathi.reporting import build_report
from netsathi import plain
from netsathi.plain import GLOSSARY
from netsathi.guidance import flow_for, OUTCOME
from netsathi.explain import local_explanation
from netsathi import ai_client
ai_client.load_env()

st.set_page_config(page_title="NetSathi", page_icon="📡", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;800&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono&display=swap');
:root{--paper:#F3F5F7;--ink:#17202A;--navy:#1F3A5F;--ok:#14706A;--warn:#8A5A00;--bad:#A8281C;--mute:#5B6773;--line:#D5DBE1}
html,body,[class*="css"]{font-family:'Source Sans 3',system-ui,sans-serif;color:var(--ink)}
h1,h2,h3{font-family:'Manrope',system-ui,sans-serif;color:var(--navy);letter-spacing:-.015em}
code,.mono{font-family:'IBM Plex Mono',Consolas,monospace;font-size:.88em}
.path{display:flex;align-items:flex-start;margin:1.2rem 0 1.6rem}
.node{flex:0 0 auto;width:150px;text-align:center}
.dot{width:44px;height:44px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;background:var(--mute)}
.node b{display:block;font-family:'Manrope',sans-serif}.node span{font-size:.85rem;color:var(--mute)}
.link{flex:1;height:3px;margin-top:21px;background:var(--line);min-width:30px}
.s-PASS .dot{background:var(--ok)}.s-FAIL .dot,.s-ERROR .dot{background:var(--bad)}.s-WARNING .dot{background:var(--warn)}
.link.bad{background:repeating-linear-gradient(90deg,var(--bad) 0 8px,transparent 8px 14px)}.link.good{background:var(--ok)}
.tag{display:inline-block;padding:1px 8px;border:1px solid var(--line);border-radius:4px;font-size:.82rem}
.lab{display:inline-block;padding:1px 8px;border-radius:4px;font-size:.8rem;font-weight:600;background:#E4EAF1;color:var(--navy);margin-right:6px}
.sim{border-left:4px solid var(--warn);padding:.5rem .9rem;background:#FFF6E3;margin-bottom:1rem}
:focus-visible{outline:3px solid var(--navy)!important;outline-offset:2px}
@media(max-width:700px){.node{width:90px}.path{overflow-x:auto}}
</style>""", unsafe_allow_html=True)

MARK = {"PASS": "✓", "FAIL": "✕", "WARNING": "!", "INCONCLUSIVE": "?", "SKIPPED": "–", "ERROR": "✕"}
WORD = {"PASS": "Worked", "FAIL": "Did not work", "WARNING": "Warning", "INCONCLUSIVE": "Unclear", "SKIPPED": "Not run", "ERROR": "Error"}
VIEWS = ["Dashboard", "Running the tests", "Results", "Guided fix", "Ask NetSathi", "Report"]
ANS = ["I did this and saw what's described", "The result looks different", "I can't find this setting", "This didn't help", "I want to skip this step"]
ss = st.session_state
for k, v in {"mode": "Live Diagnosis", "results": None, "prev": None, "note": None, "run": False, "step": 0, "view": "Dashboard", "history": [], "glog": {}, "symptom_saved": None, "chat": []}.items(): ss.setdefault(k, v)
go = lambda v: ss.update(view=v)
def reset(): ss.update(results=None, prev=None, note=None, run=False, step=0, history=[], glog={}, chat=[])
def retest(): ss.update(run=True, view="Running the tests")
def save_ans(key, title): ss.glog[title] = ss[key]

with st.sidebar:
    st.markdown("## NetSathi")
    st.caption("Find out why the internet isn't working, one step at a time.")
    st.radio("Go to", VIEWS, key="view")
    mode = st.radio("Where do results come from?", ["Live Diagnosis", "Demo Mode"], key="mode_sel", help="Live runs real tests on this computer. Demo Mode shows made-up results so you can present without internet.")
    if mode != ss.mode: ss.mode = mode; reset(); st.rerun()
    scenario = fixed = None
    if mode == "Demo Mode":
        scenario = st.selectbox("Demo scenario", list(SCENARIOS), key="scenario")
        fixed = st.checkbox("On retest, pretend the fix worked", key="demo_fixed", help="Simulated. Lets you demo a successful retest.")
    win = st.selectbox("Your Windows version", ["Windows 11", "Windows 10", "Something else"], key="win", help="We show menu paths for your version.")
    st.divider()
    st.caption("Session: " + ("no results yet" if not ss.results else f"{len(ss.history)} test run(s)"))
    st.caption("NetSathi only reads your settings. It never changes them.")

WV = "10" if win == "Windows 10" else "11"
def path_html(res):
    r = {c.id: c.status.value for c in res} if res else {}
    nodes = [("local", "This computer"), ("gateway", "Router"), ("external", "Internet"), ("dns", "Website lookup")]
    out = ""
    for i, (k, n) in enumerate(nodes):
        s = r.get(k, "SKIPPED") if res else "SKIPPED"
        out += f'<div class="node s-{s}"><div class="dot">{MARK[s]}</div><b>{n}</b><span>{WORD[s] if res else "Not tested"}</span></div>'
        if i < 3:
            nxt = r.get(nodes[i + 1][0]); cls = "bad" if nxt in ("FAIL", "ERROR") else "good" if nxt == "PASS" and s == "PASS" else ""
            out += f'<div class="link {cls}"></div>'
    return f'<div class="path" role="img" aria-label="Test results from your computer to the router, the internet and website lookup">{out}</div>'

def check_rows(res, show_limits=False):
    for c in res:
        st.markdown(f"**{MARK[c.status.value]} {plain.title(c)}**: {WORD[c.status.value]}  \n<span class='mono'>{c.observed}</span>", unsafe_allow_html=True)
        st.caption(f"Technical name: {plain.tech(c)}. " + (plain.limits(c) if show_limits else ""))

def run_checks():
    if ss.results: ss.prev = ss.results
    try:
        if ss.mode == "Demo Mode":
            ss.results = SCENARIOS["Everything works"] if (ss.prev and fixed) else SCENARIOS[scenario]
            st.write("Loaded simulated results. Nothing was measured.")
        else:
            out = []
            with st.status("Running tests. This takes up to about 30 seconds.", expanded=True) as stt:
                for fn in ALL_CHECKS:
                    r = fn(); out.append(r)
                    st.markdown(f"**{MARK[r.status.value]} {plain.title(r)}**: {WORD[r.status.value]}  \n<span class='mono'>{r.observed}</span>", unsafe_allow_html=True)
                stt.update(label="Tests finished", state="complete")
            ss.results = out
        ss.note = compare(ss.prev, ss.results) if ss.prev else None
        ss.history.append(diagnose(ss.results).title); ss.step = 0
    except Exception:
        ss.results = ss.prev
        st.error("The tests could not finish. Nothing was changed on your computer. Try again, or switch to Demo Mode to see how NetSathi works.")

def need_results():
    if not ss.results:
        st.info("There are no results yet. Start a diagnosis on the Dashboard first."); st.button("Go to Dashboard", on_click=go, args=("Dashboard",)); return True

if ss.mode == "Demo Mode": st.markdown('<div class="sim"><b>Demo mode.</b> Every result here is simulated. Nothing was measured on your computer.</div>', unsafe_allow_html=True)
v = ss.view
if v == "Dashboard":
    st.title("Find out why your internet isn't working")
    st.write("Pick what you're seeing. NetSathi runs a few safe tests, explains the result in plain words, and shows you exactly where to click.")
    symptom = st.radio("What's happening?", ["I'm connected to Wi-Fi but have no internet", "Websites won't load", "Websites won't load but other apps work (possible address-book, or DNS, problem)", "I think the problem is my router or my computer's connection", "My internet is slow or keeps cutting out (limited check)"], key="symptom")
    if symptom.startswith("My internet is slow"): st.warning("One test can't catch a problem that comes and goes. NetSathi runs the same tests once and may miss it.")
    st.subheader("What NetSathi will test")
    st.markdown("1. Whether your computer has an address on the network.\n2. Whether the device that links you to other networks answers (usually your router).\n3. Whether a well-known internet address answers a small test message.\n4. Whether your computer can find a website's address.")
    st.caption("Nothing is changed. The tests take up to about 30 seconds.")
    st.markdown(path_html(None) if False else "", unsafe_allow_html=True)
    def start(): reset(); ss.symptom_saved = ss.symptom; ss.run = True; ss.view = "Running the tests"
    st.button("Start diagnosis", type="primary", on_click=start, help="Runs the tests now.")
    if ss.history: st.caption("This session: " + "; ".join(ss.history))
elif v == "Running the tests":
    st.title("Running the tests")
    if ss.run:
        ss.run = False; run_checks()
        if ss.results:
            st.markdown(path_html(ss.results), unsafe_allow_html=True)
            if ss.note: st.info(ss.note)
            st.button("See what we found", type="primary", on_click=go, args=("Results",))
    elif ss.results:
        check_rows(ss.results); st.button("See what we found", type="primary", on_click=go, args=("Results",))
    else: st.info("Nothing is running. Press Start diagnosis on the Dashboard.")
elif v == "Results" and not need_results():
    dx = diagnose(ss.results, simulated=ss.mode == "Demo Mode")
    tags = ('<span class="lab">Simulated result</span>' if dx.simulated else "") + f'<span class="lab">Certainty: {dx.certainty}</span>'
    st.title(dx.title); st.markdown(tags, unsafe_allow_html=True); st.markdown(path_html(ss.results), unsafe_allow_html=True)
    if ss.note:
        (st.success if "resolved" in ss.note else st.warning)("Compared with your last test: " + ss.note)
        if "still" in ss.note: st.write(OUTCOME.get(dx.key, OUTCOME["default"]))
    st.header("1. What we found"); st.write(dx.found)
    st.header("2. What this means for you"); st.write(local_explanation(dx))
    st.header("3. Why we think this")
    for c in ss.results:
        lab = plain.LABEL[c.status.value]
        st.markdown(f'<span class="lab">{lab}</span> {plain.line(c)}', unsafe_allow_html=True)
        if c.status.value != "PASS": st.caption(plain.limits(c))
    for x in dx.causes: st.markdown(f'<span class="lab">Possible cause</span> {x}', unsafe_allow_html=True)
    st.header("4. What to do next")
    t, why, steps = flow_for(dx)
    st.markdown(f'<span class="lab">Recommended action</span> {t}: {len(steps)} short steps.', unsafe_allow_html=True)
    st.button("Open the step-by-step guide", type="primary", on_click=go, args=("Guided fix",))
    st.header("5. How to check whether it worked"); st.write(dx.verify)
    st.button("Retest now", on_click=retest, help="Runs the tests again and compares.")
    st.button("Ask a question about this result", on_click=go, args=("Ask NetSathi",))
    with st.expander("Technical details and limits"):
        for c in ss.results: st.write(f"**{plain.tech(c)}** ({c.duration_s}s): {c.observed}. {c.explanation}")
        for x in dx.limitations: st.write("• " + x)
    with st.expander("What does this mean? Plain-language glossary"):
        for k, x in GLOSSARY.items(): st.write(f"**{k}**: {x}")
elif v == "Guided fix" and not need_results():
    dx = diagnose(ss.results); t, why, steps = flow_for(dx)
    st.title(t); st.write(why); st.caption("You do these steps yourself. NetSathi changes nothing. Menu names can differ between Windows versions, computer makers and work or school settings." + (" These steps are written for Windows, so your menus may differ." if win == "Something else" else ""))
    i = min(ss.step, len(steps) - 1); stp = steps[i]
    st.progress((i + 1) / len(steps), text=f"Step {i + 1} of {len(steps)}")
    st.subheader(stp["title"]); st.markdown(f"**Why we ask:** {stp['purpose']}")
    for n, line in enumerate(stp["how"][WV], 1): st.write(f"{n}. {line}")
    st.markdown(f"**What you should see:** {stp['look_for']}")
    if stp["retest"]:
        st.button("Retest now", type="primary", on_click=retest)
    else:
        key = f"ans_{dx.key}_{i}"
        a = st.radio("What happened?", ANS, index=None, key=key, on_change=save_ans, args=(key, stp["title"]))
        if a == ANS[0]: st.success(stp["if_ok"])
        elif a == ANS[1]: st.warning(stp["if_not"])
        elif a == ANS[2]: st.info("Try this instead: " + stp["alt"])
        elif a == ANS[3]: st.warning("Thanks. We'll note that this didn't help. " + stp["if_not"])
        elif a == ANS[4]: st.info("Skipped. We'll note it in your report.")
        with st.expander("What does this mean?"):
            for k, x in GLOSSARY.items(): st.write(f"**{k}**: {x}")
    c1, c2 = st.columns(2)
    if i > 0: c1.button("Previous", on_click=lambda: ss.update(step=i - 1))
    if i < len(steps) - 1: c2.button("Continue", type="primary", disabled=(not stp["retest"] and ss.get(f"ans_{dx.key}_{i}") is None), on_click=lambda: ss.update(step=i + 1), help="Pick what happened first.")
    else: st.write("**After this:** " + OUTCOME.get(dx.key, OUTCOME["default"]))
elif v == "Ask NetSathi":
    st.title("Ask NetSathi")
    st.markdown('<span class="lab">AI explanation</span> Answers here explain and suggest. They are not test results. NetSathi\'s tests and rules decide the diagnosis.', unsafe_allow_html=True)
    st.caption("Privacy: when you send a question, it is processed by Ollama's cloud service. Before sending, NetSathi hides IP addresses, device addresses (MAC), website names and your user and computer name. Nothing is sent until you press Enter.")
    ok = ai_client.is_configured()
    if not ok:
        st.info("The AI assistant is off because no Ollama API key is set. The rest of NetSathi still works.")
        with st.expander("How to switch it on"):
            st.markdown("1. Create a free key at ollama.com/settings/keys.\n2. In the NetSathi folder, copy `.env.example` to a new file named `.env`.\n3. Open `.env` in Notepad and put your key after `OLLAMA_API_KEY=`.\n4. Stop NetSathi (Ctrl+C in PowerShell) and start it again.")
    has = bool(ss.results)
    use_ctx = st.checkbox("Include my test results (private details hidden)", value=has, disabled=not has, key="chat_ctx")
    if not has: st.caption("There are no test results yet, so answers will be general guidance. Run a diagnosis first if you want answers about your connection.")
    for m in ss.chat:
        with st.chat_message(m["role"]): st.write(m["content"])
    q = st.chat_input("Ask about your internet problem", disabled=not ok, max_chars=ai_client.MAX_QUESTION)
    if q:
        with st.chat_message("user"): st.write(q)
        ctx = ai_client.build_context(ss.results, diagnose(ss.results, ss.mode == "Demo Mode")) if (has and use_ctx) else ""
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."): res = ai_client.ask(q, ss.chat, ctx)
            if res.ok:
                st.write(res.text); st.caption("AI explanation, not a test result.")
                ss.chat = (ss.chat + [{"role": "user", "content": q}, {"role": "assistant", "content": res.text}])[-2 * ai_client.MAX_HISTORY:]
            else: st.error(res.message + " Your question was not saved. You can try again.")
    if ss.chat: st.button("Clear chat", on_click=lambda: ss.update(chat=[]))
elif v == "Report" and not need_results():
    dx = diagnose(ss.results, simulated=ss.mode == "Demo Mode"); st.title("Your report")
    st.markdown('<span class="lab">Simulated result</span>' if dx.simulated else '<span class="lab">Real result</span>', unsafe_allow_html=True)
    st.write(f"**{dx.title}**"); st.write(dx.found)
    for f in dx.why: st.markdown(f"• {f}")
    if ss.note: st.info("Retest: " + ss.note)
    if ss.glog: st.write("Steps you reported: " + "; ".join(f"{k}: {x}" for k, x in ss.glog.items()))
    st.download_button("Download report (JSON file)", build_report(ss.symptom_saved, ss.results, dx, ss.note, [f"{k}: {x}" for k, x in ss.glog.items()]), "netsathi_report.json", "application/json", type="primary")
    st.caption("The report holds test results, your Windows type and plain-language advice. No passwords, keys or website contents.")
