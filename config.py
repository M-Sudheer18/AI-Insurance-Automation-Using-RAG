import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Loading Key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Secret Key for Flask
SECRET_KEY = os.getenv("SECRET_KEY", "chat_scholar_secret_key")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Application Information
APP_NAME = "Insurance Claim System"
APP_VERSION = "1.0.0"

# Directories
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_FOLDER = BASE_DIR / "documents"
UPLOADS_FOLDER   = BASE_DIR / "uploads"
VECTOR_DB_FOLDER = BASE_DIR / "vector_db"

# Gemini AI Configuration
LLM_MODEL = "gemini-3.6-flash"
TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 2048

# Embedding Configuration
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"

# Text Splitter Configuration
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Retriever Configuration
SEARCH_TYPE = "mmr"
TOP_K = 5
FETCH_K = 20
LAMBDA_MULT = 0.7

# Uploads
ALLOWED_EXTENSIONS = {"pdf"}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024   # 50 MB

# Logging Configuration
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.DEBUG if FLASK_DEBUG else logging.INFO,
    format=LOGGING_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "app.log")
    ]
)