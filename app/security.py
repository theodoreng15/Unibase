from cryptography.fernet import Fernet
import os

_cipher = Fernet(os.getenv("FERNET_KEY"))

def encrypt_key(key: str) -> str:
    raw_bytes = key.encode(encoding="utf-8")

    return _cipher.encrypt(raw_bytes).encode(encoding="utf-8")

def decrypt_token(token: bytes) -> str:
    token_bytes = token.encode(encoding="utf-8")
        
    return _cipher.decrypt(token_bytes).decode(encoding="utf-8")
