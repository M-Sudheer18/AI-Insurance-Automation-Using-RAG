import logging
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from config import DOCUMENTS_FOLDER
logger = logging.getLogger(__name__)

# Loads all PDF documents from the Documents directory.
class DocumentsLoader:
    def __init__(self):
        self.documents_path = Path(DOCUMENTS_FOLDER)

    # Load all PDF documents.
    def load_documents(self) -> list:
        documents = []
        if not self.documents_path.exists():
            logger.error(f"Documents directory missing: {self.documents_path}")
            raise FileNotFoundError(
                f"Documents folder not found: {self.documents_path}"
            )
        
        # Get all Pdf Files
        pdf_files = sorted(self.documents_path.glob("*.pdf"))
        # Check if PDFs exist
        if not pdf_files:
            logger.warning(f"No PDF files discovered in: {self.documents_path}")
            raise FileNotFoundError(
                f"No PDF files found in: {self.documents_path}"
            )
        logger.info(f"Initializing load sequence for {len(pdf_files)} file(s).")
        
        # Load each PDF
        for pdf_file in pdf_files:
            try:
                logger.info("Processing document: %s", pdf_file.name)
                loader = PyMuPDFLoader(str(pdf_file))
                file_docs = loader.load()
                documents.extend(file_docs)
                logger.info(
                    "Successfully loaded %d pages from %s",
                    len(file_docs),
                    pdf_file.name,
                )
            except Exception as e:
                logger.exception(
                    "Failed to process %s. Error: %s",
                    pdf_file.name,
                    str(e),
                )
                continue

        logger.info(f"Document Loading Complete. Total Pages Extracted {len(documents)}")
        if not documents:
            logger.error("No documents could be loaded successfully.")
            raise RuntimeError("Failed to load any valid PDF documents.")
        return documents