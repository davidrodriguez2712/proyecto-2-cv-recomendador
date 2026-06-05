from database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Boolean, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import VECTOR
from pydantic import BaseModel, Field

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key= True, index= True)
    username = Column(String, unique= True, nullable= False)
    email = Column(String, unique=True, nullable= False)
    rol = Column(String, nullable= False)
    name = Column(String, nullable= True)
    hashed_password = Column(String, nullable= False)
    lastname = Column(String, nullable= True)

class MemoryLongTermResume(Base):
    __tablename__ = "memory_resume"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    message = Column(String)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate= func.now())

class MemoryLongTermVectors(Base):
    __tablename__ = "memory_vector"
    user_id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    embedding_vector = Column(Integer)
    create_date = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON)

class Token(BaseModel):
    access_token: str
    token_type: str


class CreateUser(BaseModel):
    user: str
    rol: str
    email: str
    name: str
    lastname: str
    hashed_password: str

class LoginRequest(BaseModel):
    username: str
    password: str



