from pathlib import Path

from src.swynex_automation.classifier import classify_file


def test_classify_file_documents():
    assert classify_file(Path("notes.txt")) == "Documents"
    assert classify_file(Path("report.PDF")) == "Documents"


def test_classify_file_unknown():
    assert classify_file(Path("mystery.abc")) == "Others"
