# Project instructions

Use the existing checkout; each cloud task is isolated. Do not create worktrees
unless requested. Use Python 3.11+ and the `.venv` environment.

Do not submit applications or implement automatic submission. Do not fabricate
applicant information. Require at least 80/100 with evidence for all criteria.
Respect site restrictions; stop on access challenges or ambiguous permissions.
Filling and uploading can transmit information: obtain human approval of the
exact answers, destination and approved resume before browser preparation.
Keep credentials, applicant records, resumes and session state out of Git.

Validation: `.venv/bin/python -m pytest`, `.venv/bin/python -m pip check`, and
`.venv/bin/python scripts/browser_smoke.py`. The smoke test uses only local HTML.
Do not visit a live application merely to validate a code change.
