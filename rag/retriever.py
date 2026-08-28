import logging
from langchain_community.vectorstores import FAISS
from config import (
    SEARCH_TYPE,
    TOP_K,
    FETCH_K,
    LAMBDA_MULT
)
from langchain_core.vectorstores import VectorStoreRetriever

logger = logging.getLogger(__name__)

class RetrieverManager:
    def __init__(self, vector_store: FAISS):
        if vector_store is None:
            logger.error("Cannot initialize RetrieverManager without a valid FAISS vector store.")
            raise ValueError("Vector store instance is required.")
        self.vector_store = vector_store

    # Configures and returns a LangChain VectorStoreRetriever using parameters from config.py.
    def get_retriever(self) -> VectorStoreRetriever:
        logger.info(
            "Initializing retriever | search_type=%s | k=%d | fetch_k=%d | lambda_mult=%.2f",   
            SEARCH_TYPE,
            TOP_K,
            FETCH_K,
            LAMBDA_MULT
        )
        try:
            search_kwargs = {
                "k": TOP_K,
                "fetch_k": FETCH_K,
                "lambda_mult": LAMBDA_MULT
            }
            retriever = self.vector_store.as_retriever(
                search_type=SEARCH_TYPE,
                search_kwargs=search_kwargs
            )
            logger.info(
                "Retriever initialized successfully using '%s' search.",
                SEARCH_TYPE
            )
            return retriever    
            
        except Exception as e:
            logger.exception("Failed to initialize retriever from vector store.")
            raise RuntimeError("Retriever initialization failed.") from e