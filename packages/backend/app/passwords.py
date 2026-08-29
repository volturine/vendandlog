import hashlib
import secrets

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    return f'scrypt${salt.hex()}${derived.hex()}'


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt_hex, digest_hex = stored.split('$')
    except ValueError:
        return False
    if algo != 'scrypt':
        return False
    derived = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    return secrets.compare_digest(derived.hex(), digest_hex)


def new_session_token() -> str:
    return secrets.token_hex(32)
