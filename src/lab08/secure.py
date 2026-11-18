import os
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from flask_jwt_extended import JWTManager

load_dotenv()

jwt = JWTManager()
PEPPER = os.getenv("PASSWORD_PEPPER")
if not PEPPER:
    raise RuntimeError("PASSWORD_PEPPER is missing from your .env")

hidden = PasswordHasher(memory_cost=65536, time_cost=4, parallelism=3)


def Hashing(password: str) -> str:
    return hidden.hash(f"{password}{PEPPER}")


def Verifier(stored_hash: str, password: str) -> bool:
    try:
        hidden.verify(stored_hash, f"{password}{PEPPER}")
        return True
    except (VerifyMismatchError, InvalidHashError):
        # wrong password, or a malformed/legacy hash in the DB -> just fail the login
        return False
