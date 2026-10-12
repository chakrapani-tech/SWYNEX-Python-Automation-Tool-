import hashlib
from pathlib import Path

from src.swynex_automation.hashing import sha256_file


def test_sha256_file(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello world", encoding="utf-8")
    digest = sha256_file(file_path)
    assert digest == hashlib.sha256(b"hello world").hexdigest()
