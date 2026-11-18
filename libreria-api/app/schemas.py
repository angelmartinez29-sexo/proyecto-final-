"""Esquemas Pydantic: validación de entrada y serialización de salida."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Editoriales ----------
class EditorialBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    pais: str | None = Field(None, max_length=60)
    sitio_web: str | None = Field(None, max_length=200)


class EditorialCreate(EditorialBase):
    pass


class EditorialOut(EditorialBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Libros ----------
class LibroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=150)
    autor: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=10, max_length=17, description="ISBN-10 o ISBN-13")
    anio_publicacion: int = Field(..., gt=1000, lt=2100)
    precio: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(0, ge=0)
    editorial_id: int = Field(..., gt=0)


class LibroCreate(LibroBase):
    pass


class LibroOut(LibroBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class LibroDetalle(LibroOut):
    """Libro con los datos completos de su editorial."""
    editorial: EditorialOut


# ---------- Autenticación ----------
class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
