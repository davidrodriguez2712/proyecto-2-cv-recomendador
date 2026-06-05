import sys
from pathlib import Path
from core.security import get_current_user, oauth2, pwd_context
from database import get_db
from fastapi import APIRouter, HTTPException, status, UploadFile, Depends, File
from typing import Annotated
from sqlalchemy.orm import Session
from schemas import User
from graph.graph_builder import GraphBuilder
from graph.react_graph_builder import ReactAgent
from core.logging_config import setup_backend_logger
from sqlalchemy import select

logger = setup_backend_logger()

router = APIRouter(
    prefix="/agent",
    tags= ["agent"]
)

db_dependecy = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/cv-upload", status_code= status.HTTP_201_CREATED)
async def cv_upload_user(db: db_dependecy, user: user_dependency, file: UploadFile = File(...)):
    try:
        # Método ASYNC
        response = await db.execute(
            select(User).where(User.username == user.get("user"))
        )
        username = response.scalar_one_or_none()

        # Método SYNC
        # user = db.query(User).filter(User.id == user.get("id_user")).first()
        if username is None:
            raise HTTPException(status_code= 401, detail= "Don't have permissions")
    except Exception as e:
        print(f"Error Authentication: {e}")
        logger.debug(f"Error Authentication: {e}")
        raise HTTPException(status_code= 404, detail= "Problem with the Authentication")
    try:
        content = await file.read()
        content_dict = {
            "content": content,
            "username": user.get("user"),
            "content_type": file.content_type,
            "name": file.filename
        }
        graph = GraphBuilder()
        #graph_execution = graph.graph_cv()
        graph_compile = graph.compile_graph()
        response = await graph_compile.ainvoke({"cv_object": content_dict})
        logger.debug(f"Response: {response}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        logger.debug(f"Error: {e}")
        raise HTTPException(status_code= 404, detail="Problem with the file uploaded")


@router.post("/general-query", status_code= status.HTTP_200_OK)
async def general_query(db: db_dependecy, user: user_dependency, query: str):
    try:
        response = await db.execute(
            select(User).where(User.username == user.get("user"))
        )
        username = response.scalar_one_or_none()
        if username is None:
            HTTPException(status_code= 401, detail="User doesn't exist")
        graph_query = ReactAgent()
        
        
    except Exception as e:
        logger.debug(f"Error in authentication: {e}")

    















