from dataclasses import dataclass, field
from enum import Enum

class Status(str, Enum):
    PASS = "PASS"; FAIL = "FAIL"; WARNING = "WARNING"
    INCONCLUSIVE = "INCONCLUSIVE"; SKIPPED = "SKIPPED"; ERROR = "ERROR"

@dataclass
class CheckResult:
    id: str
    name: str
    status: Status
    observed: str
    explanation: str = ""
    duration_s: float = 0.0
    simulated: bool = False

@dataclass
class Diagnosis:
    key: str                 # dns | local | gateway_silent | upstream | ok | inconclusive
    title: str
    found: str               # what we found
    meaning: str             # what it means for you
    certainty: str           # likely | possible | inconclusive | no problem observed
    why: list = field(default_factory=list)       # evidence that triggered the rule
    causes: list = field(default_factory=list)    # possible causes (inferred)
    verify: str = ""         # how to check it worked
    facts: list = field(default_factory=list)
    limitations: list = field(default_factory=list)
    simulated: bool = False
    @property
    def summary(self): return self.meaning
