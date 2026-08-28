import logging
import fitz  # PyMuPDF
from pathlib import Path

logger = logging.getLogger(__name__)

# class for extracting text from uploaded claim documents.
class PDFReader:
    # Extracts raw text from a given PDF file path.
    @staticmethod
    def extract_text(file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            logger.error("Upload file not found at %s", file_path)
            raise FileNotFoundError(f"Could Not Locate File: {file_path}")

        logger.info("Initializing text extraction for: %s", path.name)
        extracted_text = []

        # Open the document using fitz (PyMuPDF)
        try:
            with fitz.open(str(path)) as doc:
                for page in doc:
                    extracted_text.append(
                        page.get_text("text")
                    )

            full_text = "\n".join(extracted_text).strip()
            if not full_text:
                logger.warning("Extracted text is empty for file: %s (May be a scanned image)", path.name)
            else:
                logger.info("Successfully extracted %d characters from %s", len(full_text), path.name)
            return full_text
        
        except Exception as e:
            logger.exception("Failed to extract text from %s. Error: %s", path.name, str(e))
            raise RuntimeError(f"PDF text extraction failed for {path.name}") from e