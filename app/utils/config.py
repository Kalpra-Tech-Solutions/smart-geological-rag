import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# LanceDB Configuration
LANCEDB_PATH = "./data/lancedb"

# Model Parameters
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
TEXT_MODEL = "llama3-8b-8192"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# File Processing
TEMP_DIR = "./temp"
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB

def validate_api_keys():
    """Check if API keys are set."""
    if not GROQ_API_KEY or not HUGGINGFACE_API_KEY:
        raise ValueError("API keys for Groq and HuggingFace must be set in the .env file.")
