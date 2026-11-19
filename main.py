#!/usr/bin/env python3
"""THE WORLD — 19 November 2026 (make.fun news-image-20261119).

Copies the bundled ``entry.png`` — one newspaper page summing up the
world news of Thursday 19 November 2026 — to
``$MAKEFUN_OUTPUT_DIR/entry.png``.

Before writing, the program verifies the file it is about to copy:
the PNG magic bytes and the SHA-256 digest must match the values the
repository was built with, so a damaged or swapped image can never be
submitted by accident.

Standard library only (pathlib + hashlib). No network, no randomness:
every run writes the same bytes.
"""
import hashlib
import os
import sys
from pathlib import Path

EXPECTED_SHA256 = "1e25e1c08c2524407f10f5a7349f0469f0c06a273ddd44ef2315007c9b8febe0"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576  # competition cap: image at most 1 MiB

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("error: MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 2

    data = SOURCE.read_bytes()

    if data[:8] != PNG_MAGIC:
        print("error: entry.png does not start with the PNG magic bytes",
              file=sys.stderr)
        return 1

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        print("error: entry.png SHA-256 mismatch: got "
              f"{digest}, expected {EXPECTED_SHA256}", file=sys.stderr)
        return 1

    if len(data) > MAX_BYTES:
        print(f"error: entry.png is {len(data)} bytes, over the "
              f"{MAX_BYTES}-byte limit", file=sys.stderr)
        return 1

    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    dest = target / "entry.png"
    dest.write_bytes(data)
    print(f"wrote {dest} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
