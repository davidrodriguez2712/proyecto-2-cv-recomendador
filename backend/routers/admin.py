from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from core.security import get_current_user
from passlib.context import CryptContext
from database import get_db, Session
from typing import Annotated, List
from schemas import User, CreateUser
from core.security import pwd_context
from sqlalchemy import select

router = APIRouter(
    prefix= "/admin",
    tags= ["admin"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/all", status_code= status.HTTP_200_OK)
async def get_all_users(db: db_dependency, user: user_dependency):
    # METODO ASYNC:
    response = await db.execute(
        select(User).where(User.username == user.get("id_user"))
    )
    userdb = response.scalar_one_or_none()

    # MÉTODO SYNC:
    # userdb = db.query(User).filter(User.id == user.get("id_user")).first()

    #response = db.query(User).all()
    if userdb is None or user.get("rol") != "admin":
        raise HTTPException(status_code= 401, detail= "Authentication Failed")
    response_all = await db.execute(
        select(User).where(User.username == "user")
    )
    response_all_list = response_all.scalars().all()

    return response_all_list

@router.post("/create", status_code= status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: user_dependency, user_form: CreateUser):
    try:
        # MÉTODO ASYNC
        response = await db.execute(
            select(User).where(User.username == user_form.user)
        )
        db_validation = response.scalar_one_or_none()

        # MÉTODO SYNC
        # db_validation = db.query(User).filter(User.id == user.get("id_user")).first()
        if db_validation is None or db_validation.rol != "admin":
            raise HTTPException(status_code=401, detail="Don't have permissions for this endpoint.")
        userdb = User(
            username = user_form.user,
            email = user_form.email,
            rol = user_form.rol,
            name = user_form.name,
            lastname = user_form.lastname,
            hashed_password = pwd_context.hash(user_form.hashed_password)
        )
        
        db.add(userdb)
        # db.commit() # método sync
        await db.commit()
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=401, detail= "Creation user Failed")
        


    






