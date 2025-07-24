import os
from dotenv import load_dotenv
from typing import Dict, Any
import glob
import time

# Load environment variables
load_dotenv()

class Config:
    """Configuration management with enhanced cleanup capabilities"""
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    
    # LanceDB Configuration
    LANCEDB_URI = os.getenv('LANCEDB_URI', 'data/geological_rag_db')
    
    # Model Configuration
    VISION_MODEL = os.getenv('VISION_MODEL', 'llama-3.2-90b-vision-preview')
    TEXT_MODEL = os.getenv('TEXT_MODEL', 'llama-3.3-70b-versatile')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    
    # Processing Configuration
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
    TEMP_DIR = os.getenv('TEMP_DIR', 'temp')
    
    @classmethod
    def validate_required_keys(cls) -> tuple[bool, str]:
        """Validate that required API keys are present"""
        if not cls.GROQ_API_KEY:
            return False, "GROQ_API_KEY is missing from .env file"
        if not cls.HUGGINGFACE_API_KEY:
            return False, "HUGGINGFACE_API_KEY is missing from .env file"
        return True, "All API keys are present"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs('data', exist_ok=True)
    
    @classmethod
    def cleanup_temp_directory(cls):
        """Clean up temp directory on startup with enhanced Windows support"""
        if not os.path.exists(cls.TEMP_DIR):
            return
        
        # Find all temp files
        temp_patterns = [
            os.path.join(cls.TEMP_DIR, "tmp*.pdf"),
            os.path.join(cls.TEMP_DIR, "tmp*.png"),
            os.path.join(cls.TEMP_DIR, "tmp*.jpg"),
            os.path.join(cls.TEMP_DIR, "tmp*.*")
        ]
        
        files_cleaned = 0
        files_failed = 0
        
        for pattern in temp_patterns:
            temp_files = glob.glob(pattern)
            for temp_file in temp_files:
                try:
                    # Multiple attempts with increasing delays
                    for attempt in range(3):
                        try:
                            os.unlink(temp_file)
                            files_cleaned += 1
                            break
                        except PermissionError:
                            if attempt < 2:
                                time.sleep(0.5 * (attempt + 1))
                            else:
                                files_failed += 1
                        except Exception:
                            files_failed += 1
                            break
                except Exception:
                    files_failed += 1
        
        if files_cleaned > 0:
            print(f"✅ Cleaned up {files_cleaned} temp files")
        if files_failed > 0:
            print(f"⚠️ Could not clean {files_failed} temp files (may be in use)")
    
    @classmethod
    def force_cleanup_temp_directory(cls):
        """Force cleanup of temp directory (more aggressive)"""
        import shutil
        
        if not os.path.exists(cls.TEMP_DIR):
            return
        
        try:
            # Try to remove entire temp directory and recreate
            shutil.rmtree(cls.TEMP_DIR, ignore_errors=True)
            time.sleep(1)  # Wait for Windows to release handles
            os.makedirs(cls.TEMP_DIR, exist_ok=True)
            print("✅ Force cleaned temp directory")
        except Exception as e:
            print(f"⚠️ Force cleanup failed: {e}")
            # Fallback to regular cleanup
            cls.cleanup_temp_directory()
