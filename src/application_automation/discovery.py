"""Import user-curated listings; automated discovery requires a site-specific review."""
import json
from pathlib import Path
from urllib.parse import urlsplit

from .models import Job


def load_jobs(path: Path) -> list[Job]:
    jobs = [Job(**row) for row in json.loads(path.read_text())]
    for job in jobs:
        url = urlsplit(job.url)
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("Job URLs must be HTTPS without embedded credentials")
    return jobs
