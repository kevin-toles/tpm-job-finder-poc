"""
ResumeParser: Extracts structured resume data from PDF, DOCX, and TXT files
Output: JSON with sections, bullets, dates, education, certs, etc.
"""
import os
from src.storage.secure_storage import SecureStorage
from typing import Dict, Any

try:
    import pdfplumber
except ImportError as e:
    from src.error_service.handler import handle_error
    handle_error(e, context={'component': 'resume_parser', 'import': 'pdfplumber'})
    pdfplumber = None
try:
    import docx
except ImportError as e:
    from src.error_service.handler import handle_error
    handle_error(e, context={'component': 'resume_parser', 'import': 'docx'})
    docx = None

class ResumeParser:
    def parse(self, file_path: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext in [".doc", ".docx"]:
            return self._parse_docx(file_path)
        elif ext == ".txt":
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        if not pdfplumber:
            raise ImportError("pdfplumber not installed")
        try:
            storage = SecureStorage()
            secure_path = storage.get_file_path(file_path)
            with pdfplumber.open(secure_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            return self._basic_structure(text)
        except Exception as e:
            from src.error_service.handler import handle_error
            handle_error(e, context={'component': 'resume_parser', 'method': '_parse_pdf', 'file_path': file_path})
            return {"error": str(e)}

    def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        if not docx:
            raise ImportError("python-docx not installed")
        try:
            storage = SecureStorage()
            secure_path = storage.get_file_path(file_path)
            doc = docx.Document(secure_path)
            text = "\n".join(p.text for p in doc.paragraphs)
            return self._basic_structure(text)
        except Exception as e:
            from src.error_service.handler import handle_error
            handle_error(e, context={'component': 'resume_parser', 'method': '_parse_docx', 'file_path': file_path})
            return {"error": str(e)}

    def _parse_txt(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            return self._basic_structure(text)
        except Exception as e:
            from src.error_service.handler import handle_error
            handle_error(e, context={'component': 'resume_parser', 'method': '_parse_txt', 'file_path': file_path})
            return {"error": str(e)}

    def _basic_structure(self, text: str) -> Dict[str, Any]:
        # Simple section and bullet extraction (can be improved)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        sections = {}
        current_section = "summary"
        sections[current_section] = []
        for line in lines:
            if line.endswith(":") and len(line.split()) < 6:
                current_section = line[:-1].lower()
                sections[current_section] = []
            elif line.startswith("-") or line.startswith("•"):
                sections.setdefault(current_section, []).append(line.lstrip("-• "))
            else:
                sections.setdefault(current_section, []).append(line)
        # Example output structure
        return {
            "sections": sections,
            "raw_text": text
        }

# Example usage:
# parser = ResumeParser()
# result = parser.parse("resume.pdf")
# print(result)
