"""Configuración de la conexión a PostgreSQL con SQLAlchemy."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/libreria"


def _normalize_database_url(raw_url: str) -> str:
    """Asegura que las URLs de PostgreSQL usen el dialecto explícito de psycopg2."""
    url = raw_url.strip()
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if (
        url.startswith("postgresql://")
        and "+psycopg2" not in url
        and "+psycopg" not in url
    ):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _get_connect_args(database_url: str) -> dict:
    """Devuelve argumentos adicionales según el motor de base de datos."""
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=_get_connect_args(DATABASE_URL),
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Clase base declarativa para los modelos ORM."""


def get_db():
    """Dependencia: abre una sesión por petición y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
