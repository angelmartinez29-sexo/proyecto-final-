"""CRUD de libros. Lectura pública; escritura protegida con token."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/libros", tags=["Libros"])


def _get_or_404(db: Session, libro_id: int) -> models.Libro:
    libro = db.get(models.Libro, libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro


def _validar_editorial(db: Session, editorial_id: int) -> None:
    if db.get(models.Editorial, editorial_id) is None:
        raise HTTPException(status_code=404, detail="La editorial indicada no existe")


@router.get("/", response_model=list[schemas.LibroOut])
def listar_libros(
    titulo: str | None = Query(None, description="Filtrar por título (contiene)"),
    autor: str | None = Query(None, description="Filtrar por autor (contiene)"),
    editorial_id: int | None = Query(None, gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(models.Libro).order_by(models.Libro.titulo)
    if titulo:
        stmt = stmt.where(models.Libro.titulo.ilike(f"%{titulo}%"))
    if autor:
        stmt = stmt.where(models.Libro.autor.ilike(f"%{autor}%"))
    if editorial_id:
        stmt = stmt.where(models.Libro.editorial_id == editorial_id)
    return db.scalars(stmt.offset(skip).limit(limit)).all()


@router.get("/{libro_id}", response_model=schemas.LibroDetalle)
def obtener_libro(libro_id: int, db: Session = Depends(get_db)):
    libro = db.scalar(
        select(models.Libro)
        .options(joinedload(models.Libro.editorial))
        .where(models.Libro.id == libro_id)
    )
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro


@router.post(
    "/",
    response_model=schemas.LibroOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def crear_libro(datos: schemas.LibroCreate, db: Session = Depends(get_db)):
    _validar_editorial(db, datos.editorial_id)
    libro = models.Libro(**datos.model_dump())
    db.add(libro)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un libro con ese ISBN")
    db.refresh(libro)
    return libro


@router.put(
    "/{libro_id}",
    response_model=schemas.LibroOut,
    dependencies=[Depends(get_current_user)],
)
def actualizar_libro(
    libro_id: int, datos: schemas.LibroCreate, db: Session = Depends(get_db)
):
    libro = _get_or_404(db, libro_id)
    _validar_editorial(db, datos.editorial_id)
    for campo, valor in datos.model_dump().items():
        setattr(libro, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un libro con ese ISBN")
    db.refresh(libro)
    return libro


@router.delete(
    "/{libro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def eliminar_libro(libro_id: int, db: Session = Depends(get_db)):
    libro = _get_or_404(db, libro_id)
    db.delete(libro)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
