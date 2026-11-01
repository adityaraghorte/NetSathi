"""Plain-language names and meanings for each check."""
CHECKS = {  # id: (plain title, technical name, what it can show, what it cannot show)
 "local": ("Your computer's connection setup", "IP address", "whether your computer has an address on the network", "whether the network itself works"),
 "gateway": ("The device that links you to other networks (usually your router)", "Default gateway", "whether that device answered a small test message", "that it is broken. Many routers ignore this kind of test"),
 "routing": ("Your computer's list of network routes", "Routing table", "whether your computer knows where to send traffic that leaves your network", "whether those routes actually work"),
 "external": ("Reaching the internet by number", "Ping to an external IP address", "whether a well-known internet address replied to a small test message", "that every website works. Some networks block this test"),
 "dns": ("Finding a website's address", "DNS lookup", "whether your computer could find the address for example.com", "why a failure happened"),
 "dns_alt": ("Asking a public address book directly", "Public DNS resolver test", "whether a separate public service (1.1.1.1) answered an address lookup", "anything about your own settings"),
}
SAYS = {"PASS": "worked", "FAIL": "did not work", "WARNING": "worked with a warning", "INCONCLUSIVE": "could not be confirmed", "SKIPPED": "was not run", "ERROR": "hit an error"}
LABEL = {"PASS": "Confirmed observation", "FAIL": "Confirmed observation", "WARNING": "Confirmed observation", "INCONCLUSIVE": "Inconclusive test", "SKIPPED": "Inconclusive test", "ERROR": "Inconclusive test"}
def title(c): return CHECKS.get(c.id, (c.name,))[0]
def tech(c): return CHECKS.get(c.id, (c.name, c.name))[1]
def line(c): return f"{title(c)} {SAYS[c.status.value]}."
def limits(c):
    t = CHECKS.get(c.id)
    return f"This test can show {t[2]}. It cannot show {t[3]}." if t else ""
GLOSSARY = {
 "IP address": "A number that identifies your device on a network.",
 "Router": "The device that connects your home or office network to other networks.",
 "Gateway": "The network device your computer normally sends traffic through to reach other networks. At home this is usually your router.",
 "DNS": "The system that helps your computer find the address of a website. It works like an address book.",
 "Ping": "A test that checks whether another device answers a small network message.",
 "Timeout": "The test did not get a reply within the allowed time.",
 "Packet loss": "Some test messages did not get replies. This can mean a network problem, or that a device ignores those tests.",
 "Network adapter": "The hardware or software part that connects your computer to a network, such as your Wi-Fi card.",
}
