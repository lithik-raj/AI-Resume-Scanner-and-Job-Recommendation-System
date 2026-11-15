from pathlib import Path
import pdfplumber


class ResumeParseError(Exception):
    """Raised when a resume cannot be parsed successfully."""
    pass


def extract_text(file_path: str) -> str:
    """
    Extract readable text from a resume (PDF or TXT).
    Fully backward-compatible with existing AI Resume Screener calls.
    """
    path = Path(file_path)

    if not path.exists():
        raise ResumeParseError(f"Resume file was not found: {file_path}")

    extension = path.suffix.lower()

    if extension == ".txt":
        try:
            return path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            try:
                return path.read_text(encoding="latin-1").strip()
            except Exception as exc:
                raise ResumeParseError(f"TXT resume could not be decoded: {exc}") from exc
        except Exception as exc:
            raise ResumeParseError(f"TXT resume could not be read: {exc}") from exc

    # Default to PDF parsing via pdfplumber
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
    except Exception as exc:
        # Fallback to fitz/PyMuPDF if available
        try:
            import fitz
            doc = fitz.open(file_path)
            pages = [page.get_text("text") for page in doc if page.get_text("text")]
            doc.close()
            text = " ".join(pages)
        except Exception:
            raise ResumeParseError(f"Resume PDF could not be opened: {exc}") from exc

    return text.strip()


# Backward compatibility alias for Resume_Fit_Scorer callers
extract_resume_text = extract_text
extract_text_from_txt = extract_text
extract_text_from_pdf = extract_text
