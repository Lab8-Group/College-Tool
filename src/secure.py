import os
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

load_dotenv()

PEPPER = os.environ['PASSWORD_PEPPER']
if not PEPPER:
    raise RuntimeError("PASSWORD_PEPPER is missing from your .env file")

hidden = PasswordHasher(memory_cost=65536, time_cost=4, parallelism=3)

def Hashing(password: str) -> str:
    peppered = f"{password}{PEPPER}"
    return hidden.hash(peppered)



def Verifier(stored_hash: str, password: str) -> bool:
    try:
        peppered = f"{password}{PEPPER}"
        hidden.verify(stored_hash, peppered)
        return True
    except VerifyMismatchError:
        return False