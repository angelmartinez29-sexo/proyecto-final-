"""Modelos SQLAlchemy (tablas de la base de datos)."""
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Editorial(Base):
    __tablename__ = "editoriales"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    pais: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)

    libros: Mapped[list["Libro"]] = relationship(
        back_populates="editorial", cascade="all, delete-orphan"
    )


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    autor: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    existencia: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    editorial_id: Mapped[int] = mapped_column(
        ForeignKey("editoriales.id", ondelete="CASCADE"), nullable=False
    )

    editorial: Mapped[Editorial] = relationship(back_populates="libros")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nomuser: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    passwd: Mapped[str] = mapped_column(String(255), nullable=False)
    nombrecompleto: Mapped[str] = mapped_column(String(150), nullable=False)
