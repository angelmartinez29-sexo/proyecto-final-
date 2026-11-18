"""Punto de entrada de la API de Librería Chiapas."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import auth, models  # noqa: F401  (models registra las tablas en Base)
from .database import Base, engine
from .routers import editoriales, libros


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas si no existen (para producción, usar Alembic)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Librería Chiapas",
    description="API REST para gestionar el catálogo de libros y editoriales.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(libros.router)
app.include_router(editoriales.router)


@app.get("/", tags=["Inicio"])
def inicio():
    return {"mensaje": "API Librería Chiapas funcionando", "docs": "/docs"}
