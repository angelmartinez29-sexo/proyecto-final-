"""CRUD de editoriales. Lectura pública; escritura protegida con token."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/editoriales", tags=["Editoriales"])


def _get_or_404(db: Session, editorial_id: int) -> models.Editorial:
    editorial = db.get(models.Editorial, editorial_id)
    if editorial is None:
        raise HTTPException(status_code=404, detail="Editorial no encontrada")
    return editorial


@router.get("/", response_model=list[schemas.EditorialOut])
def listar_editoriales(
    nombre: str | None = Query(None, description="Filtrar por nombre (contiene)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(models.Editorial).order_by(models.Editorial.nombre)
    if nombre:
        stmt = stmt.where(models.Editorial.nombre.ilike(f"%{nombre}%"))
    return db.scalars(stmt.offset(skip).limit(limit)).all()


@router.get("/{editorial_id}", response_model=schemas.EditorialOut)
def obtener_editorial(editorial_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, editorial_id)


@router.get("/{editorial_id}/libros", response_model=list[schemas.LibroOut])
def libros_de_editorial(editorial_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, editorial_id).libros


@router.post(
    "/",
    response_model=schemas.EditorialOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def crear_editorial(datos: schemas.EditorialCreate, db: Session = Depends(get_db)):
    editorial = models.Editorial(**datos.model_dump())
    db.add(editorial)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una editorial con ese nombre")
    db.refresh(editorial)
    return editorial


@router.put(
    "/{editorial_id}",
    response_model=schemas.EditorialOut,
    dependencies=[Depends(get_current_user)],
)
def actualizar_editorial(
    editorial_id: int, datos: schemas.EditorialCreate, db: Session = Depends(get_db)
):
    editorial = _get_or_404(db, editorial_id)
    for campo, valor in datos.model_dump().items():
        setattr(editorial, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una editorial con ese nombre")
    db.refresh(editorial)
    return editorial


@router.delete(
    "/{editorial_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def eliminar_editorial(editorial_id: int, db: Session = Depends(get_db)):
    editorial = _get_or_404(db, editorial_id)
    if editorial.libros:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: la editorial tiene libros registrados",
        )
    db.delete(editorial)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
