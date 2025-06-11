from passlib.context import CryptContext
import re
# Configuração do bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str) -> bool:
    """
    Valida se a senha tem pelo menos 8 caracteres, uma letra maiúscula e um caractere especial.
    """
    if (len(password) < 8 or
        not re.search(r"[A-Z]", password) or
        not re.search(r"[^a-zA-Z0-9]", password)):
        return False
    return True