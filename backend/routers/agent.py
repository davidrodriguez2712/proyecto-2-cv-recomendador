import sys
from pathlib import Path
from core.security import get_current_user, oauth2, pwd_context
from database import get_db
from fastapi import APIRouter, HTTPException, status, UploadFile, Depends, File
from typing import Annotated
from sqlalchemy.orm import Session
from schemas import User, GeneralQueryRequest, GeneralQueryResponse
from graph.graph_builder import GraphBuilder
from graph.react_graph_builder import ReactAgent
from core.logging_config import setup_backend_logger
from sqlalchemy import select
from langchain_core.messages import HumanMessage, AIMessage

logger = setup_backend_logger()

react_agent = ReactAgent()
react_graph_instance = react_agent.compile_react()

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


async def process_general_query(request: GeneralQueryRequest, username: str) -> GeneralQueryResponse:
    messages = []
    for msg in request.history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    
    messages.append(HumanMessage(content=request.query))

    config = {"recursion_limit": 10}
    result = await react_graph_instance.ainvoke(
        {"messages": messages, "user": username},
        config=config
    )

    all_messages = result.get("messages", [])
    last_message = all_messages[-1] if all_messages else AIMessage(content="No se pudo generar respuesta.")
    
    tools_used = []
    for m in all_messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                tname = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                if tname and tname not in tools_used:
                    tools_used.append(tname)

    return GeneralQueryResponse(
        response=last_message.content,
        tools_used=tools_used
    )

@router.post("/general-query", response_model=GeneralQueryResponse, status_code=status.HTTP_200_OK)
async def general_query(db: db_dependecy, user: user_dependency, data: GeneralQueryRequest):
    try:
        response = await db.execute(
            select(User).where(User.username == user.get("user"))
        )
        username = response.scalar_one_or_none()
        if username is None:
            raise HTTPException(status_code=401, detail="User doesn't exist")
        
        return await process_general_query(data, username=user.get("user"))

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error procesando general query: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno procesando la consulta: {str(e)}")

    















