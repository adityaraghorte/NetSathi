"""Scenario-specific, manual troubleshooting flows. NetSathi never performs these for the user.
Menu paths are for Windows 11 and 10 and can differ by device, version or organisation settings."""
from .plain import GLOSSARY

def S(title, purpose, how, look, ok, no, alt, retest=False):
    return dict(title=title, purpose=purpose, how=how, look_for=look, if_ok=ok, if_not=no, alt=alt, retest=retest)
W = lambda w11, w10=None: {"11": w11, "10": w10 or w11}

NOTE = "Menu names can differ between Windows versions, computer makers and work or school settings."
RECONNECT = S("Turn Wi-Fi off and on again", "A fresh connection often fixes a connection that has gone stale.",
  W(["Click the Wi-Fi icon at the right end of the taskbar (near the clock).", "Click the Wi-Fi button so it turns off. Wait 10 seconds.", "Click it again to turn Wi-Fi on, then click the arrow next to it and choose your network."],
    ["Click the Wi-Fi icon at the right end of the taskbar.", "Click your network name, then Disconnect. Wait 10 seconds.", "Click your network name again, then Connect."]),
  "Your network name with the word 'Connected' under it.", "Good. Go to the next step.", "If it asks for a password, enter your Wi-Fi password. If it won't connect, choose 'This didn't help'.",
  "No Wi-Fi icon? Open Start > Settings > Network & internet and check Airplane mode is off. A laptop may also have a Wi-Fi key or switch on its keyboard or side.")
VIEW_SETUP = S("Look at your connection details (look only)", "To see whether your computer was given an address. You only look. You don't change anything.",
  W(["Click Start, then Settings.", "Click Network & internet, then Wi-Fi.", "Click your connected network's 'Properties' (or 'Hardware properties').", "Scroll to 'IPv4 address' and 'IPv4 DNS servers'."],
    ["Click Start, then Settings.", "Click Network & Internet, then Status.", "Under your connected network, click Properties.", "Scroll to 'IPv4 address' and 'IPv4 DNS servers'."]),
  "An 'IPv4 address' made of four numbers, such as 192.168.1.20. It should not start with 169.254.", "Good. Your computer has an address. Go to the next step.",
  "If the address is blank or starts with 169.254, your computer didn't get an address from the network. Choose 'The result looks different' and continue.",
  "Can't find it? In the Settings search box, type 'View network properties'. On a wired connection choose Ethernet instead of Wi-Fi.")
TROUBLESHOOTER = S("Run the Windows network troubleshooter", "Windows has a built-in helper that checks common problems safely.",
  W(["Click Start, then Settings.", "Click System, then Troubleshoot.", "Click Other troubleshooters.", "Next to 'Network and Internet', click Run."],
    ["Click Start, then Settings.", "Click Update & Security, then Troubleshoot.", "Click Additional troubleshooters.", "Click 'Internet Connections', then 'Run the troubleshooter'."]),
  "A window that checks and then says whether it found a problem.", "If it found and fixed something, go to the next step and retest.",
  "If it reports a problem it can't fix, choose 'This didn't help' and continue. Some fixes ask for administrator permission.",
  "Can't find it? Use the Settings search box and type 'troubleshoot network'. It may be hidden on work or school computers.")
OTHER_DEVICE = S("Check another device on the same network", "This shows whether the problem is only on this computer or on the whole network.",
  W(["Take a phone or another computer that is on the same Wi-Fi.", "Open a website you haven't visited recently."]),
  "Whether the other device loads the website.", "If the other device also fails, the problem is probably outside this computer. Go to the next step.",
  "If the other device works, the problem is probably on this computer. Choose 'The result looks different' and return to the earlier steps.",
  "No other device? Skip this step.")
RESTART_ROUTER = S("Restart your router (only if it is yours)", "A restart clears many temporary router faults. Use this only on a home or office router you control.",
  W(["Find the router (the box with blinking lights).", "Unplug its power cable. Wait 30 seconds.", "Plug it back in. Wait about 2 minutes until the lights settle."]),
  "Steady lights, usually including an internet or globe light.", "Go to the next step and retest.",
  "If the internet light stays red, orange or off, contact your internet provider.", "Not your router? Skip this step and contact the network administrator.")
FLUSH = S("Clear the stored website addresses (optional)", "Your computer keeps a short memory of website addresses. A bad entry can cause trouble. Clearing it is safe and reversible.",
  W(["Click Start, type 'Command Prompt', then click 'Run as administrator' if you have it. (A normal window may show an error.)", "Type exactly: ipconfig /flushdns", "Press Enter."]),
  "The message: Successfully flushed the DNS Resolver Cache.", "Good. Go to the next step.",
  "If you see 'Function failed during execution', you don't have administrator permission. Skip this step or restart your computer instead.",
  "No administrator access? Restart your computer (Start > Power > Restart). It clears the same memory.")
DNS_LOOK = S("Check which address book your computer uses (look only)", "To see whether the address-book service setting looks normal. Don't change it yet.",
  W(["Click Start, then Settings, then Network & internet, then Wi-Fi.", "Click 'Hardware properties' (or your network's Properties).", "Find 'DNS server assignment' and 'IPv4 DNS servers'."], ["Open Settings, Network & Internet, Status, then Properties under your network.", "Find 'IPv4 DNS servers'."]),
  "One or more numbers, or 'Automatic (DHCP)'. Automatic is normal on most networks.", "If it says Automatic, go to the next step.",
  "If a server is listed that you or someone else set by hand, ask whoever set it up before changing it. Changing it can stop other things working.",
  "Can't find it? Skip this step. Don't change anything you don't understand.")
RETEST = S("Run NetSathi again", "To check, with a real test, whether the steps helped.", {"11": ["Press 'Retest now' below."], "10": ["Press 'Retest now' below."]},
  "NetSathi shows a comparison with your earlier result.", "If it shows the problem is resolved, you're done.", "If it is still there, contact your network administrator or internet provider and give them the NetSathi report.",
  "Not sure? Download the report from the Report page and share it.", retest=True)

FLOWS = {
 "dns": ("Fix a website address problem", "Your computer reached the internet but couldn't find website addresses.", [RECONNECT, DNS_LOOK, FLUSH, TROUBLESHOOTER, RETEST]),
 "local": ("Fix your computer's connection setup", "Your computer doesn't seem to have a complete connection setup.", [RECONNECT, VIEW_SETUP, TROUBLESHOOTER, RESTART_ROUTER, RETEST]),
 "gateway_silent": ("Find out if the problem is the router or your computer", "The router didn't answer and the internet test failed.", [OTHER_DEVICE, RECONNECT, RESTART_ROUTER, RETEST]),
 "upstream": ("Work out whether the problem is outside your computer", "Your computer has an address but can't confirm the internet.", [OTHER_DEVICE, RESTART_ROUTER, TROUBLESHOOTER, RETEST]),
 "inconclusive": ("Get a clearer result", "NetSathi couldn't tell what is wrong.", [RECONNECT, VIEW_SETUP, RETEST]),
 "ok": ("If the problem comes back", "The tests worked this time.", [S("Test again while the problem is happening", "A problem that comes and goes can be missed.", W(["Wait until the problem happens again.", "Open NetSathi and run a diagnosis straight away."]),
        "Results that differ from this one.", "Follow the guide NetSathi then shows.", "If it never fails during a test, the problem may be with one website or app. Contact its support.", "You can also download the report.", retest=True)]),
}
OUTCOME = {"dns": "If the retest still shows the website-address problem, ask your network administrator or internet provider about the address (DNS) service.",
           "default": "If the retest still shows a problem, contact your network administrator or internet provider and share the NetSathi report."}
def flow_for(dx): return FLOWS[dx.key]
def steps_for(dx): return FLOWS[dx.key][2]
