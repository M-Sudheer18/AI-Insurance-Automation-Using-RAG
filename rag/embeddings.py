import logging
from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class EmbeddingsManager:
    def __init__(self):
        logger.info(f"Initializing Hugging Face Embeddings with Model: {EMBEDDING_MODEL}")
        try:
            # We set normalize_embeddings=True, which is recommended for BGE models to use cosine similarity.
            self.embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                encode_kwargs={
                    "normalize_embeddings": True
                }
            )
            logger.info("Embedding Model Loaded Successfully ")
        except Exception as e:
            logger.exception("Failed to initialize embedding model.")
            raise RuntimeError(
                "Embedding model initialization failed."
            )

# Returns the initialized embedding model to be used by the Vector Store.
    def get_embeddings(self) -> HuggingFaceEmbeddings:
        return self.embeddings