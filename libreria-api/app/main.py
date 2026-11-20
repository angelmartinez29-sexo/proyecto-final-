"""Punto de entrada de la API de Librería Chiapas."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

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

# Endpoints públicos de autenticación (/auth/login y /auth/registro)
app.include_router(auth.router)

# Todos los endpoints de libros y editoriales exigen Bearer Token válido
app.include_router(
    libros.router,
    dependencies=[Depends(auth.get_current_user)],
)
app.include_router(
    editoriales.router,
    dependencies=[Depends(auth.get_current_user)],
)


@app.get("/", tags=["Inicio"])
def inicio():
    return {"mensaje": "API Librería Chiapas funcionando", "docs": "/docs"}
