import os
import logging
from pathlib import Path
from config import VECTOR_DB_FOLDER
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self, embeddings: HuggingFaceEmbeddings):
        self.embeddings = embeddings
        self.persist_directory = str(VECTOR_DB_FOLDER)
        self.vector_store = None

    # Creates a new FAISS vector store from a list of documents and saves it locally.
    def create_vector_store(self, documents: list[Document]) -> FAISS:
        if not documents:
            logger.error("No documents provided for vector store creation.")
            raise ValueError("Documents are required.")
        logger.info("Creating FAISS vector store from %d document chunks...", len(documents))

        try:
            self.vector_store = FAISS.from_documents(
                documents,
                self.embeddings
            )
            logger.info("FAISS vector store created successfully.")
            return self.vector_store
        except Exception as e:
            logger.exception("Failed to Create Faiss Vector Store")
            raise RuntimeError("Vector Store Creation Failed") from e

    def load_vector_store(self) -> FAISS:
        index_path = Path(self.persist_directory) / "index.faiss"

        if not index_path.exists():
            logger.warning("No Existing FAISS index found")
            return None

        try:
            self.vector_store = FAISS.load_local(
                folder_path=self.persist_directory,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Existing FAISS vector store loaded successfully.")
            return self.vector_store
        except Exception as e:
            logger.exception("Failed to load vector store.")
            raise RuntimeError("Vector store loading failed.")
        
    # Saves the current FAISS vector store to the local disk
    def save_local(self):
        if self.vector_store is None:
            logger.error("No Vector Store Exists in Disk")
            return
        try:
            self.vector_store.save_local(self.persist_directory)
            logger.info(
                "FAISS vector store saved successfully to %s",
                self.persist_directory
            )
        except Exception as e:
            logger.exception("Failed to save the FAISS vector store.")
            raise RuntimeError("Vector store saving failed.") from e

    # Returns a retriever interface from the loaded vector store.
    def get_vector_store(self) -> FAISS:
        return self.vector_store