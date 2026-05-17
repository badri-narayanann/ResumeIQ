from pathlib import Path

from extractors import allowed_file, extract_text


def test_allowed_file_accepts_supported_extensions():
    assert allowed_file("resume.pdf")
    assert allowed_file("resume.docx")
    assert allowed_file("resume.txt")


def test_allowed_file_rejects_unsupported_extensions():
    assert not allowed_file("resume.exe")
    assert not allowed_file("resume.zip")


def test_extract_text_returns_text_for_txt_file(tmp_path: Path):
    test_file = tmp_path / "resume.txt"
    test_file.write_text("Python developer with SQL experience", encoding="utf-8")

    extracted = extract_text(str(test_file))
    assert "Python developer with SQL experience" in extracted
