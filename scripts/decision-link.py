#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Decision-Link CLI: Link decisions.yaml entries to observability_db.py sessions.

This is the command-line entry point for the decision-link functionality.
The core logic is in lib/decision_link.py for testability.
"""

import argparse
import sys
from pathlib import Path

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from decision_link import DecisionLinker


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Link decisions.yaml entries to observability DB sessions"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=str(
            Path.home()
            / ".claude"
            / "plugins"
            / "contextune"
            / "data"
            / "observability.db"
        ),
        help="Path to observability.db (default: ~/.claude/plugins/contextune/data/observability.db)",
    )
    parser.add_argument(
        "--decisions",
        type=str,
        default="decisions.yaml",
        help="Path to decisions.yaml (default: decisions.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write changes to decisions.yaml",
    )

    args = parser.parse_args()

    linker = DecisionLinker(
        db_path=args.db, decisions_path=args.decisions, dry_run=args.dry_run
    )
    linker.run()


if __name__ == "__main__":
    main()
