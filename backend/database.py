from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(), override= True)

url_bd = os.getenv("URL_DATABASE")

# engine = create_engine(url_bd) # forma síncrona (sync)

# forma asíncrona
engine = create_async_engine(
    url_bd,
    pool_pre_ping= True,
    pool_recycle= 300,
)

# Forma Síncrona (sync)
#SessionLocal = sessionmaker(bind=engine, autoflush= False, autocommit = False)
# sessionmaker es la plantilla que define como se crean las conexiones a la bd
# su propósito es crear instancias de Session configuradas a tu conexión

# Forma Asíncrona
SessionLocal = sessionmaker(
    bind= engine,
    class_= AsyncSession,
    expire_on_commit= False,
    autoflush= False,
    autocommit = False
)

# -------------------------------------
# Forma asíncrona (async), si fuera sync solo necesitaríamos esta línea debajo
Base = declarative_base()
# es una función que crea una clase base a partir de la cual definirás todos tus modelos ORM (tus tablas).
# Toda clase (tabla) que herede de esta Base será reconocida por SQLAlchemy 
# como parte del esquema de la base de datos.

# Forma asíncrona (async) se requiere tanto lo de abajo como la variable Base
# se debe invokar en el main.py y antes de iniciar Fastapi o inicio del servidor
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# -------------------------------------

# Función síncrona (sync)
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# Función asíncrona
async def get_db():
    async with SessionLocal() as session:
        yield session







