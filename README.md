# ApplicationAutomation

Python 3.11+ tools for truthful, human-reviewed job application preparation.
Socket's Ashby application is the first pilot. **Application submission is disabled.**

## Setup

Use the existing checkout; cloud tasks are already isolated and do not need a worktree.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# If system Chromium is absent, install the Playwright-managed browser:
# .venv/bin/python -m playwright install chromium
cp .env.example .env
.venv/bin/application-automation init
.venv/bin/python -m pytest
.venv/bin/python scripts/browser_smoke.py
```

The CLI reads exported process variables, not `.env` automatically. Set
`APPLICATION_DATA_DIR` to change the local database directory. No credentials are
required for the scaffold. Never put credentials, session cookies, applicant data,
or resumes in tracked files. `data/`, `resumes/`, `.env`, and `artifacts/` are ignored;
keep private files there and check `git status` before committing.

## Modules and gates

- `discovery`: imports a curated JSON array of jobs with `id`, `company`, `title`,
  and an HTTPS `url`. It performs no crawling.
- `scoring`: weighted, evidence-backed criteria produce a score out of 100.
  At least **80/100** and evidence for every criterion are required. Unknown facts
  block qualification; the scaffold does not infer applicant qualifications.
- `resumes`: selects an existing PDF or DOCX whose SHA-256 matches a human-approved
  variant. It never generates, edits, or embellishes applicant information.
- `approvals`: time-limited human approvals bind an action to the exact payload.
  Approval objects must come from an actual reviewer; code-generated approval
  records alone do not constitute human consent.
- `forms`: Playwright preparation for the Socket Ashby pilot, with exact field
  labels mapped to applicant-supplied facts. Uploads and filling require approval
  because pages may autosave. No submission action is implemented.
- `tracking`: SQLite event history with job IDs, statuses, and timestamps only.
- `cli`: `init` initializes local tracking; `status` lists recorded events.

## Socket pilot procedure

1. Supply the exact Socket job listing URL and verify its company, role, and current
   availability. `config/socket-pilot.example.json` is intentionally incomplete.
2. Review the site's terms and automation restrictions. Stop on a restriction,
   CAPTCHA, login/access barrier, or uncertainty; do not bypass protections.
3. Supply verified applicant facts and approved resume variants. Evaluate explicit
   weighted criteria and record evidence. Scores below 80 or missing evidence stop
   preparation. Do not invent answers to required fields.
4. Inspect the actual form and map each accessible label to a verified fact.
   Present the exact URL, answers, resume hash, upload label, and site review to
   the applicant. Obtain approval for that exact `prepare_form` payload with an
   expiry. Do not create an approval on the applicant's behalf.
5. Use a headed Playwright browser under human supervision and pass its page to
   `prepare_socket_pilot`. The adapter does not click buttons or solve challenges.
   If the form requires navigation or unsupported controls, stop for review.
6. Review every filled field and attachment with the applicant. The function
   returns `awaiting_final_review`; `submit_application` always raises.
   Any eventual submission must be performed manually by the applicant.

Example payload keys for `content_digest`: `url`, `fields` (label-to-answer map),
`resume_sha256`, `resume_label`, and `site_review`. Keep the payload and approval
private. Approvals are an application-layer guard, not an authentication system.

## Validation and limitations

`python -m pytest` exercises scoring boundaries, missing evidence, altered resumes,
expired/mismatched approvals, SQLite persistence, and the preparation boundary
using a fake page. A separate local Chromium smoke check verifies the installed
browser without visiting a job site. Live Ashby preparation remains unverified
until the listing, applicant materials, site review, and approvals are supplied.
The smoke script uses `CHROMIUM_EXECUTABLE`, system `chromium`, or the installed
Playwright browser, in that order. This cloud machine was validated with
`/usr/bin/chromium`; a managed-browser download was blocked by network policy.
The draft requests `cdn.playwright.dev` access for optional browser downloads.
Network installs and Chromium launches may require execution outside the command
sandbox; keep the configured proxy and TLS verification. Headed use additionally
requires an interactive display, which has not been validated here.

This is a scaffold: no discovery API, login handling, automatic scoring model,
interactive approval UI, or end-to-end orchestration is implemented.
