"""Score only explicitly evaluated criteria; unknown evidence blocks qualification."""
from dataclasses import dataclass
import math

QUALIFICATION_THRESHOLD = 80


@dataclass(frozen=True)
class Criterion:
    name: str
    weight: float
    match: float | None
    evidence: str = ""


@dataclass(frozen=True)
class Qualification:
    score: float
    eligible: bool
    missing_evidence: tuple[str, ...]


def qualify(criteria: list[Criterion]) -> Qualification:
    if not criteria or len({c.name for c in criteria}) != len(criteria):
        raise ValueError("Provide distinct, nonempty criteria")
    for c in criteria:
        if not c.name.strip() or not math.isfinite(c.weight) or c.weight <= 0:
            raise ValueError("Each criterion needs a name and positive finite weight")
        if c.match is not None and (not math.isfinite(c.match) or not 0 <= c.match <= 1):
            raise ValueError("Match must be between zero and one")
    missing = tuple(c.name for c in criteria if c.match is None or not c.evidence.strip())
    score = 100 * sum(c.weight * (c.match or 0) for c in criteria) / sum(c.weight for c in criteria)
    return Qualification(score, not missing and score >= QUALIFICATION_THRESHOLD, missing)
