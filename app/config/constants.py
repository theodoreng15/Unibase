from pathlib import Path
import os
from dotenv import load_dotenv

# ---------- Storage ----------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")
STORAGE_ROOT = (BASE_DIR / "storage").resolve()
TEMP_STORAGE_ROOT = (BASE_DIR / "tmp_storage").resolve()
STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local")
DELETE_LOCAL_CHUNKS_AFTER_SUCCESS = os.getenv(
    "DELETE_LOCAL_CHUNKS_AFTER_SUCCESS", "0"
).strip().lower() in ("1", "true", "yes", "y")

# ---------- MongoDB ----------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "unibase")
MONGO_MANIFESTS_COLLECTION = os.getenv("MONGO_MANIFESTS_COLLECTION", "manifests")
MONGO_CHUNKS_COLLECTION = os.getenv("MONGO_CHUNKS_COLLECTION", "chunks")

# ---------- Chunking ----------
DEFAULT_CHUNK_SIZE = 256 * 1024     # 256 KiB
READ_SIZE = 64 * 1024               # 64 KiB streaming read
ENABLED_CHUNK_PROVIDERS = tuple(
    p.strip().lower()
    for p in os.getenv("ENABLED_CHUNK_PROVIDERS", "gd,box,dropbox").split(",")
    if p.strip()
)

# ---------- Hashing ----------
HASH_ALGORITHM = "sha256"

# ---------- HTTP ----------
DEFAULT_CONTENT_TYPE = "application/octet-stream"
