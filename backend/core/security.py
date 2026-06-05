from fastapi import Depends, APIRouter, Path, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
#from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import Base, SessionLocal, get_db
from schemas import User, Token, LoginRequest
from typing import Annotated, List
import os
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import logging
from core.logging_config import setup_backend_logger
from sqlalchemy import select

logger = setup_backend_logger()

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

pwd_context = CryptContext(
    schemes= ["bcrypt"],
    deprecated = "auto",
)

KEY = os.getenv("KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token") # Extrae automaticamente el token JWT del encabezado HTTP

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[str, Depends(oauth2)]

def create_token(id_user: int, rol: str, user: str, expires_delta: timedelta):
    #response = db.query(User).filter(User.id == id_user).first() 
    timedelta = datetime.now(timezone.utc) + expires_delta
    token = jwt.encode({
        "id_user": id_user,
        "rol": rol,
        "user": user,
        "exp": timedelta,
    }, algorithm= ALGORITHM, key= KEY)
    return token

async def validate_user(db: db_dependency, user: str, password: str):
#def validate_user(db: db_dependency, user: str, password: str):
    # user = db.query(User).filter(User.username == user).first() # sync method
    result = await db.execute(
        select(User).where(User.username == user)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2)]):
    try:
        payload = jwt.decode(token, algorithms= [ALGORITHM], key= KEY)
        id_user = payload.get("id_user")
        rol = payload.get("rol")
        user = payload.get("user")
        if user is None:
            raise HTTPException(status_code=401, detail="User doesn exist")
        return {"id_user": id_user, "rol": rol, "user": user}

    except JWTError:
        raise HTTPException(status_code=401, detail="Authentication Failed")

#user_dependency = Annotated[str, Depends(get_current_user)]

@router.post("/token", response_model= Token, status_code= status.HTTP_200_OK)
async def login(db: db_dependency, data: LoginRequest):
    
    try: 
        # MÉTODO ASYNC:
        response = await db.execute(
            select(User).where(User.username == data.username)
        )
        user = response.scalar_one_or_none()

        # MÉTODO SYNC:
        # user = validate_user(db= db, user= data.username, password= data.password)
        # user = db.query(User).filter(User.user == form_data.username).first()
        # if user is None:
        #     raise HTTPException(status_code= 401, detail="User doesnt exist")
        # password_validate = pwd_context.verify(form_data.password, user.hashed_password)
        # if not password_validate:
        #     raise HTTPException(status_code= 401, detail= "Password is wrong.")
        token = create_token(id_user=user.id, rol= user.rol, user=user.username, expires_delta= timedelta(minutes=30))
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.debug(f"Error identificado: {e}")
        #logger.debug(f"Datos del usuario traido de la base: {user}")

# @router.post("/token_antiguo", response_model= Token, status_code= status.HTTP_200_OK)
# async def login(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
#     user = validate_user(db= db, user= form_data.username, password= form_data.password)
#     # user = db.query(User).filter(User.user == form_data.username).first()
#     # if user is None:
#     #     raise HTTPException(status_code= 401, detail="User doesnt exist")
#     # password_validate = pwd_context.verify(form_data.password, user.hashed_password)
#     # if not password_validate
#     #     raise HTTPException(status_code= 401, detail= "Password is wrong.")
#     token = create_token(id_user=user.id, rol= user.rol, user=user.username, expires_delta= timedelta(minutes=30))
#     return {"access_token": token, "token_type": "bearer"}














