"""Preparation only. No submit, click, JavaScript, or arbitrary locator operations.

Opening a live page and filling fields can transmit information or trigger autosave.
Review site restrictions and approve the exact preparation payload first.
"""
from dataclasses import dataclass
from urllib.parse import urlsplit

from .approvals import Approval, require_approval
from .models import Applicant, Job
from .resumes import ResumeVariant
from .scoring import Qualification


@dataclass(frozen=True)
class Field:
    label: str
    fact_key: str


def prepare_socket_pilot(*, page, job: Job, applicant: Applicant,
                         qualification: Qualification, fields: list[Field],
                         resume: ResumeVariant, resume_label: str,
                         site_review: str, approval: Approval) -> str:
    url = urlsplit(job.url)
    if (job.company.casefold() != "socket" or url.scheme != "https"
            or url.hostname != "jobs.ashbyhq.com" or url.username or url.password
            or not url.path.startswith("/socket/") or url.fragment or url.query):
        raise ValueError("Provide the verified Socket Ashby job URL")
    if not qualification.eligible or qualification.score < 80 or qualification.missing_evidence:
        raise PermissionError("Qualification requires at least 80/100 with complete evidence")
    if not site_review.strip():
        raise PermissionError("Document site permission/restrictions before automation")
    if not fields or len({f.label for f in fields}) != len(fields) or not resume_label.strip():
        raise ValueError("Provide unique field labels and a resume input label")
    values = {}
    for field in fields:
        value = applicant.facts.get(field.fact_key)
        if not field.label.strip() or not value or not value.strip():
            raise ValueError(f"Missing verified fact for {field.fact_key}")
        values[field.label] = value
    resume_path = resume.verify()
    payload = {"url": job.url, "fields": values, "resume_sha256": resume.approved_sha256,
               "resume_label": resume_label, "site_review": site_review}
    require_approval(approval, "prepare_form", payload)
    page.goto(job.url, wait_until="domcontentloaded")
    # Stop on unexpected redirects rather than supplying personal information elsewhere.
    if page.url != job.url:
        raise PermissionError("Unexpected redirect; human review required")
    for label, value in values.items():
        page.get_by_label(label, exact=True).fill(value)
    page.get_by_label(resume_label, exact=True).set_input_files(str(resume_path))
    return "awaiting_final_review"


def submit_application(*args, **kwargs):
    raise PermissionError("Submission is disabled; final review and manual submission are required")
