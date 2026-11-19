#!/usr/bin/env python3
"""Publish the front-page image for make.fun news-image-20261119.

Reads the bundled ``entry.png`` that sits next to this file, checks that
it is a genuine 1024x1024 PNG under 1 MiB, and copies it byte-for-byte to
``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output`` when the variable is unset).
Everything is deterministic: the same input always produces the same
output, and the program prints the SHA-256 so any run can be compared.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
WANT_W, WANT_H = 1024, 1024


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_png_dimensions(data):
    """Return (width, height) from the IHDR chunk of a PNG byte string."""
    if len(data) < 33:
        fail("file too short to be a PNG")
    if data[:8] != PNG_MAGIC:
        fail("bad PNG magic bytes")
    length, ctype = struct.unpack(">I4s", data[8:16])
    if ctype != b"IHDR" or length != 13:
        fail("first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", data[16:24])
    bit_depth, colour_type = data[24], data[25]
    if bit_depth != 8 or colour_type not in (2, 6):
        fail(f"unexpected IHDR: bit depth {bit_depth}, colour type {colour_type}")
    return width, height


def main():
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        fail(f"missing bundled image: {source}")

    data = source.read_bytes()
    if len(data) > MAX_BYTES:
        fail(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    width, height = read_png_dimensions(data)
    if (width, height) != (WANT_W, WANT_H):
        fail(f"expected {WANT_W}x{WANT_H}, got {width}x{height}")
    digest = hashlib.sha256(data).hexdigest()

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(data)

    # Re-read the copy and confirm it matches the source exactly.
    copied = target.read_bytes()
    if hashlib.sha256(copied).hexdigest() != digest:
        fail("copied file hash does not match the source")
    if len(copied) != len(data):
        fail("copied file size does not match the source")

    print(f"entry.png: {width}x{height}, {len(data)} bytes")
    print(f"sha256: {digest}")
    print(f"wrote: {target}")


if __name__ == "__main__":
    main()
