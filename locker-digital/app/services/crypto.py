# Criptografia (SHA-256 y Ed25519)

import base64
import hashlib
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import RawEncoder

# Calcula el hash SHA-256 de un archivo dado su ruta
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

# Genera un par de claves Ed25519 (privada y pública)
def generate_ed25519_keypair() -> tuple[bytes, bytes]:
    sk = SigningKey.generate()
    vk = sk.verify_key
    return sk.encode(encoder=RawEncoder), vk.encode(encoder=RawEncoder)

# Firma un hash hexadecimal con la clave privada Ed25519
def sign_hash_hex(private_key_raw: bytes, hash_hex: str) -> bytes:
    sk = SigningKey(private_key_raw, encoder=RawEncoder)
    return sk.sign(hash_hex.encode("utf-8")).signature

# Verifica una firma Ed25519 contra un hash hexadecimal y una clave pública
def verify_hash_hex(public_key_raw: bytes, hash_hex: str, signature: bytes) -> bool:
    vk = VerifyKey(public_key_raw, encoder=RawEncoder)
    try:
        vk.verify(hash_hex.encode("utf-8"), signature)
        return True
    except Exception:
        return False

# Funciones de codificación y decodificación en Base64
def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")

# Decodifica una cadena Base64 a bytes
def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("utf-8"))