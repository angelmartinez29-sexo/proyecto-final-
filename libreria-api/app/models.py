"""Modelos SQLAlchemy (tablas de la base de datos)."""
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Editorial(Base):
    __tablename__ = "editoriales"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    pais: Mapped[str | None] = mapped_column(String(60))
    sitio_web: Mapped[str | None] = mapped_column(String(200))

    libros: Mapped[list["Libro"]] = relationship(back_populates="editorial")


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    autor: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    anio_publicacion: Mapped[int] = mapped_column(Integer, nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    editorial_id: Mapped[int] = mapped_column(
        ForeignKey("editoriales.id"), nullable=False
    )

    editorial: Mapped[Editorial] = relationship(back_populates="libros")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
