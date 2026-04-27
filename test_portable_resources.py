#!/usr/bin/env python3
"""Check whether the portable EXE can see bundled FFmpeg resources."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def find_ffmpeg(base_dir: Path) -> Path | None:
    """Find ffmpeg.exe in expected portable locations."""
    candidates = [
        base_dir / "_internal" / "bin" / "ffmpeg.exe",
        base_dir / "bin" / "ffmpeg.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    """Validate bundled FFmpeg visibility for a portable build."""
    if len(sys.argv) > 1:
        exe_path = Path(sys.argv[1]).resolve()
        base_dir = exe_path.parent
    else:
        base_dir = Path.cwd()
        exe_path = base_dir / "WMV_to_SmartTV.exe"

    print(f"EXE: {exe_path}")
    print(f"Base dir: {base_dir}")

    ffmpeg_path = find_ffmpeg(base_dir)
    if ffmpeg_path is None:
        print("FAIL: ffmpeg.exe not found in _internal/bin or bin")
        return 1

    print(f"Found FFmpeg: {ffmpeg_path}")

    result = subprocess.run(
        [str(ffmpeg_path), "-version"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        print("FAIL: ffmpeg.exe exists but failed to start")
        if result.stderr.strip():
            print(result.stderr.strip())
        return 1

    first_line = result.stdout.splitlines()[0] if result.stdout else "unknown version"
    print(f"OK: {first_line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
