#!/usr/bin/env python3
"""Round 3 entry for make.fun news-image-20261119.

THE WORLD front page for 19 November 2026, led by the ICJ Rohingya
verdict. Stdlib only: this program copies the bundled entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png after validating it byte for byte.
"""
import hashlib
import os
import struct
import sys
import zlib

EXPECTED_SHA256 = "8742f058552a163f32dbda4a6365fa074582ae2884cbce4fcc227d26927ace37"
MAX_BYTES = 1048576
MAX_DIM = 1024


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    return 1


def validate(data):
    """Check PNG magic, IHDR, chunk CRCs, size and SHA-256."""
    if len(data) > MAX_BYTES:
        return "file larger than 1 MiB"
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return "bad PNG magic bytes"
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        return "SHA-256 mismatch"
    pos = 8
    seen_ihdr = False
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data):
            return f"truncated chunk {ctype!r}"
        body = data[pos + 8:pos + 8 + length]
        crc = struct.unpack(">I", data[pos + 8 + length:end])[0]
        if zlib.crc32(ctype + body) & 0xFFFFFFFF != crc:
            return f"bad CRC in chunk {ctype!r}"
        if ctype == b"IHDR":
            if length != 13:
                return "bad IHDR length"
            w, h, depth, colour = struct.unpack(">IIBB", body[:10])
            if depth != 8 or colour not in (2, 6):
                return "IHDR must be 8-bit truecolour"
            if w > MAX_DIM or h > MAX_DIM:
                return "image larger than 1024x1024"
            seen_ihdr = True
        pos = end
        if ctype == b"IEND":
            break
    if not seen_ihdr:
        return "missing IHDR"
    return None


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "entry.png"), "rb") as f:
        data = f.read()
    err = validate(data)
    if err is not None:
        return fail(err)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"wrote {out_path} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
