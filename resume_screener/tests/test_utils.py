from utils import safe_filename


def test_safe_filename_normalizes_names():
    filename = safe_filename("..\bad?name*.pdf")
    assert "resume" not in filename or "badname" in filename
    assert filename.endswith(".pdf")
    assert ".." not in filename


def test_safe_filename_is_unique():
    first = safe_filename("resume.pdf")
    second = safe_filename("resume.pdf")
    assert first != second
