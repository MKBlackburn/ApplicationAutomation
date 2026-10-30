"""Local, explicitly approved resume variants. No resume generation or fact invention."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True)
class ResumeVariant:
    name: str
    path: Path
    approved_sha256: str

    def verify(self) -> Path:
        path = self.path.resolve(strict=True)
        if path.suffix.lower() not in {".pdf", ".docx"}:
            raise ValueError("Use a PDF or DOCX resume")
        if sha256(path.read_bytes()).hexdigest() != self.approved_sha256:
            raise ValueError("Resume content has changed or is not approved")
        return path
