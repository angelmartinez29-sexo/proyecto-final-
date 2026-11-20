"""Esquemas Pydantic: validación de entrada y serialización de salida."""
from pydantic import BaseModel, ConfigDict, Field


# ---------- Editoriales ----------
class EditorialBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    pais: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=150)


class EditorialCreate(EditorialBase):
    pass


class EditorialOut(EditorialBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Libros ----------
class LibroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    autor: str = Field(..., min_length=1, max_length=150)
    isbn: str = Field(..., min_length=1, max_length=30, description="ISBN del libro")
    anio: int = Field(..., gt=1000, lt=2100)
    existencia: int = Field(0, ge=0)
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
    nomuser: str = Field(..., min_length=3, max_length=80)
    passwd: str = Field(..., min_length=6, max_length=72)
    nombrecompleto: str = Field(..., min_length=1, max_length=150)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nomuser: str
    nombrecompleto: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
