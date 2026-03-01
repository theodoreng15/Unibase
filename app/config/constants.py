from pathlib import Path

# ---------- Storage ----------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_ROOT = (BASE_DIR / "storage").resolve()

# ---------- Chunking ----------
DEFAULT_CHUNK_SIZE = 256 * 1024     # 256 KiB
READ_SIZE = 64 * 1024               # 64 KiB streaming read

# ---------- Hashing ----------
HASH_ALGORITHM = "sha256"

# ---------- HTTP ----------
DEFAULT_CONTENT_TYPE = "application/octet-stream"