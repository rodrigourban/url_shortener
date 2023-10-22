from enum import unique
from importlib.metadata import requires
from operator import index
from sqlalchemy import Boolean, Column, Integer, String

from .database import Base

class URL(Base):
  __tablename__ = "urls"

  id = Column(Integer, primary_key=True)
  key = Column(String, unique=True, index=True) # part of the shortened url
  secret_key = Column(String, unique=True, index=True) # for statistics
  target_url = Column(String, index=True)
  is_active = Column(Boolean, default=True)
  clicks = Column(Integer, default=0)

