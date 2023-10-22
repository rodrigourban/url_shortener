import secrets # PEP506 recommends secrets instead of random
import string
from sqlalchemy.orm import Session


from . import crud

def generate_key(length: int = 5) -> str:
  chars = string.ascii_uppercase + string.digits
  return "".join(
    secrets.choice(chars) for _ in range(length)
  )

def generate_unique_key(db: Session) -> str:
  key = generate_key()
  while crud.get_db_url_by_key(db, key):
    key = generate_key()
  
  return key
    