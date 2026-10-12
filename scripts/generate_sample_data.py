from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "input"
    source.mkdir(exist_ok=True)
    for i in range(3):
        (source / f"file_{i}.txt").write_text(f"File {i}\n", encoding="utf-8")
    (source / "copy.txt").write_text("File 0\n", encoding="utf-8")
    (source / "photo.jpg").write_bytes(b"fakejpg")
    print(f"Sample data created in {source}")


if __name__ == "__main__":
    main()
