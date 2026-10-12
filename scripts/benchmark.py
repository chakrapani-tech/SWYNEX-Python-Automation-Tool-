from __future__ import annotations

import time
from pathlib import Path

from src.swynex_automation.discovery import discover_files


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "input"
    source.mkdir(exist_ok=True)
    for index in range(100):
        (source / f"bench_{index}.txt").write_text(f"benchmark sample {index}\n", encoding="utf-8")
    start = time.perf_counter()
    files = discover_files(source, recursive=True)
    elapsed = time.perf_counter() - start
    print(f"Discovered {len(files)} files in {elapsed:.4f}s")
    print(f"Throughput: {len(files) / max(elapsed, 1e-9):.2f} files/s")


if __name__ == "__main__":
    main()
