from fastapi import status, Depends, routing, FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

from routers import admin

PARENT_DIRECTORY = Path.cwd().parent
sys.path.append(f"{str(PARENT_DIRECTORY)}/proyect1/backend")
print(sys.path)

from core.request_logger import RequestloggerMiddleware
from core import security
from routers import agent
from database import Base, engine, init_db
from core.logging_config import setup_backend_logger
from dotenv import load_dotenv, find_dotenv
import asyncio
from contextlib import asynccontextmanager

load_dotenv(find_dotenv(), override= True)

logger = setup_backend_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación...")
    await init_db()
    print("Base de datos Lista")
    yield
    print("Apagando aplicación...")

app = FastAPI(lifespan= lifespan)

# asyncio.run(init_db()) # <----- esto crea las tablas en async

app.add_middleware(RequestloggerMiddleware) # para que capture los logs de cada endpoint que se ejecuta
# CORS para permitir que Streamlit llame a FASTAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], # donde corre streamlit # Cambiar por su endpoint en producción del streamlit
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers = ["*"],
)

# Crear las tablas sino existen
## Función síncrona
# Base.metadata.create_all(bind = engine)

## Función asíncrona
### La función async es lo que esta ubicado arriba llamado: asyncio.run(init_db())

app.include_router(router= security.router)
app.include_router(router= admin.router)
app.include_router(router=agent.router)

















