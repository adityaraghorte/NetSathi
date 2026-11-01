from .models import CheckResult as C, Status as S
def _c(i, n, st, o): return C(i, n, st, o, simulated=True)
SCENARIOS = {
 "DNS failure": [_c("local","Local IP configuration",S.PASS,"Local IPv4 192.168.1.20"),_c("gateway","Default gateway",S.PASS,"Gateway 192.168.1.1: ping ok"),
   _c("external","External IP reachability",S.PASS,"1.1.1.1: ok"),_c("dns","DNS resolution",S.FAIL,"example.com: gaierror")],
 "Local configuration problem": [_c("local","Local IP configuration",S.WARNING,"Link-local address 169.254.3.4"),_c("gateway","Default gateway",S.FAIL,"No default gateway configured"),
   _c("external","External IP reachability",S.FAIL,"1.1.1.1: no_reply"),_c("dns","DNS resolution",S.FAIL,"example.com: gaierror")],
 "Inconclusive": [_c("local","Local IP configuration",S.PASS,"Local IPv4 10.0.0.5"),_c("gateway","Default gateway",S.INCONCLUSIVE,"ping no_reply"),
   _c("external","External IP reachability",S.FAIL,"1.1.1.1: no_reply"),_c("dns","DNS resolution",S.PASS,"example.com -> 93.184.216.34")],
 "Everything works": [_c("local","Local IP configuration",S.PASS,"Local IPv4 192.168.1.20"),_c("gateway","Default gateway",S.PASS,"Gateway 192.168.1.1: ping ok"),
   _c("external","External IP reachability",S.PASS,"1.1.1.1: ok"),_c("dns","DNS resolution",S.PASS,"example.com -> 93.184.216.34")],
}
