#!/usr/bin/env python3
"""Copy the finished poster to the output folder and verify the copy.

The poster itself is rendered by render_poster.py into entry.png next to
this file. This script's only job is delivery: it copies entry.png into the
output directory, then checks the copy is a faithful, usable PNG before
reporting success.

The output directory comes from the MAKEFUN_OUTPUT_DIR environment variable
when set, and falls back to /output otherwise. Only the Python standard
library is used, and nothing here touches the network.

Checks performed on the delivered file:
  * it exists and is byte-identical to the source (matching SHA-256),
  * it is at most 1 MiB,
  * it starts with the PNG magic bytes,
  * its IHDR chunk reports 1024x1024 pixels.

How it works, step by step:
  1. Locate entry.png next to this file and refuse to continue if it is
     missing, so a half-built entry can never be delivered by accident.
  2. Read the source's own dimensions first: if the rendered poster is
     not 1024x1024, stop before anything is copied anywhere.
  3. Copy the file into the output directory (created if needed) and
     flush it to disk, then run every check above on the delivered copy.
  4. Print the source path, output path, SHA-256, byte count and
     dimensions, ending with "verification: OK" on success.
"""

import hashlib
import os
import shutil
import struct
import sys

MAX_BYTES = 1048576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sha256_of(path):
    """Return the hex SHA-256 digest of the file at path."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_png_size(path):
    """Return (width, height) from a PNG file's IHDR chunk.

    Reads only the 33-byte header, so it stays fast even on large files,
    and raises ValueError with a plain message if the file is not a PNG
    or has no IHDR chunk where one is expected.
    """
    with open(path, "rb") as handle:
        head = handle.read(33)
    if head[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file (bad magic bytes)")
    if len(head) < 33 or head[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk")
    return struct.unpack(">II", head[16:24])


def verify_png(path, source_digest):
    """Check the delivered file; raise SystemExit with a message on failure."""
    if not os.path.isfile(path):
        sys.exit("verification failed: output file missing: %s" % path)
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        sys.exit("verification failed: output is %d bytes, over the 1 MiB "
                 "limit" % size)
    if sha256_of(path) != source_digest:
        sys.exit("verification failed: output is not byte-identical to "
                 "entry.png")
    try:
        width, height = read_png_size(path)
    except ValueError as exc:
        sys.exit("verification failed: %s" % exc)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        sys.exit("verification failed: PNG is %dx%d, expected %dx%d"
                 % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT))
    return size, width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        sys.exit("entry.png not found next to main.py; run "
                 "render_poster.py first")
    try:
        src_width, src_height = read_png_size(source)
    except ValueError as exc:
        sys.exit("entry.png is not a usable PNG: %s" % exc)
    if (src_width, src_height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        sys.exit("entry.png is %dx%d, expected %dx%d; re-render it first"
                 % (src_width, src_height, EXPECTED_WIDTH, EXPECTED_HEIGHT))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, "entry.png")
    source_digest = sha256_of(source)
    shutil.copyfile(source, destination)
    with open(destination, "ab") as handle:
        handle.flush()
        os.fsync(handle.fileno())
    size, width, height = verify_png(destination, source_digest)
    print("source: %s" % source)
    print("output: %s" % destination)
    print("sha256: %s" % source_digest)
    print("bytes: %d" % size)
    print("dimensions: %dx%d" % (width, height))
    print("verification: OK")


if __name__ == "__main__":
    main()
