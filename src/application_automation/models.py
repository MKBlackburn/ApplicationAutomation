from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    id: str
    company: str
    title: str
    url: str


@dataclass(frozen=True)
class Applicant:
    # Only facts explicitly supplied or verified by the applicant.
    facts: dict[str, str]
