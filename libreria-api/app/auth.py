"""Configuración de la conexión a PostgreSQL con SQLAlchemy."""

import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Fuerza UTF-8 en libpq/psycopg2 en Windows antes de cargar el driver
os.environ.setdefault("PGCLIENTENCODING", "UTF8")

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Busca .env en la carpeta del proyecto (o padre si está anidada)
BASE_DIR = Path(__file__).resolve().parent.parent
for candidate in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
    if candidate.exists():
        load_dotenv(dotenv_path=candidate, encoding="utf-8")
        break
else:
    load_dotenv(encoding="utf-8")

DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/libreria"


def _normalize_database_url(raw_url: str) -> str:
    """Normaliza la URL de PostgreSQL para psycopg2 y asegura SSL en hosts remotos."""
    url = raw_url.strip().strip('"').strip("'")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif (
        url.startswith("postgresql://")
        and "+psycopg2" not in url
        and "+psycopg" not in url
    ):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    # Si es un host remoto (como Render) y no especifica sslmode, agrega sslmode=require
    if host and host not in {"localhost", "127.0.0.1", "::1"}:
        query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query_params.setdefault("sslmode", "require")
        new_query = urlencode(query_params)
        url = urlunparse(parsed._replace(query=new_query))

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
