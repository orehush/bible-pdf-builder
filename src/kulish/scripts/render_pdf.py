#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render PrinceXML-ready HTML into PDF.")
    parser.add_argument("source", type=Path, help="Rendered HTML file")
    parser.add_argument("-o", "--output", type=Path, default=Path("kulish.pdf"))
    parser.add_argument("--prince", default="prince", help="PrinceXML executable (default: prince)")
    args = parser.parse_args()

    if not args.source.exists():
        raise SystemExit(f"HTML file not found: {args.source}")

    prince = shutil.which(args.prince)
    if prince is None:
        raise SystemExit(
            "PrinceXML was not found. Install PrinceXML and make sure `prince` is available in PATH."
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = [prince, "--javascript", str(args.source), "-o", str(args.output)]
    print("Running:", " ".join(command))
    subprocess.run(command, check=True)
    print(f"Created: {args.output}")


if __name__ == "__main__":
    main()
