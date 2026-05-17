import logging

logger = logging.getLogger(__name__)

PYPDF_OK = False
PYPDF2_OK = False
try:
    from pypdf import PdfReader

    PYPDF_OK = True
except Exception as exc:
    logger.warning("pypdf unavailable: %s", exc)
    try:
        import PyPDF2  # type: ignore

        PYPDF2_OK = True
    except Exception as exc2:
        logger.warning("PyPDF2 unavailable: %s", exc2)

try:
    import docx2txt

    DOCX_OK = True
except Exception as exc:
    DOCX_OK = False
    logger.warning("docx2txt unavailable: %s", exc)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "pdf",
        "docx",
        "txt",
    }


def extract_text(filepath: str) -> str:
    text = ""
    ext = filepath.rsplit(".", 1)[1].lower()
    try:
        if ext == "pdf" and PYPDF_OK:
            with open(filepath, "rb") as handle:
                reader = PdfReader(handle)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + " "
        elif ext == "pdf" and PYPDF2_OK:
            import PyPDF2  # type: ignore

            with open(filepath, "rb") as handle:
                reader = PyPDF2.PdfReader(handle)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + " "
        elif ext == "docx" and DOCX_OK:
            text = docx2txt.process(filepath) or ""
        elif ext == "txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
    except Exception as exc:
        logger.warning("Failed to extract text from %s: %s", filepath, exc)
    return text.strip()
