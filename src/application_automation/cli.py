import argparse
import os
from pathlib import Path

from .tracking import Tracker


def main():
    parser = argparse.ArgumentParser(description="Human-reviewed job application preparation")
    parser.add_argument("command", choices=["init", "status"])
    args = parser.parse_args()
    tracker = Tracker(Path(os.environ.get("APPLICATION_DATA_DIR", "data")) / "applications.sqlite3")
    if args.command == "init":
        print("Local tracking initialized. Submission is disabled.")
    else:
        for job_id, status in tracker.events():
            print(f"{job_id}: {status}")


if __name__ == "__main__":
    main()
