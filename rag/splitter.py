import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_OVERLAP, CHUNK_SIZE
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class TextSplitter:
    # The separators list prioritizes natural breaks: paragraphs, then lines, then sentences.
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", "(?<=\\. )", " ", ""],
            is_separator_regex=True
        )

    # Takes a list of LangChain Document objects and splits them into smaller chunks.
    def split_documents(self, documents: list[Document]) -> list[Document]:
        if not documents:
            logger.warning("No Documents Provided to Splitter")
            return []
        logger.info("Initiating text splitting for %d document pages...", len(documents))

        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(
                "Successfully split documents into %d chunks (Size: %d, Overlap: %d).",
                len(chunks),
                CHUNK_SIZE,
                CHUNK_OVERLAP
            )
            return chunks
        except Exception:
            logger.exception("Failed during text splitting.")
            raise RuntimeError("Text splitting failed.")