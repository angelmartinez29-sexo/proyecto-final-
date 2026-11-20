"""Autenticación con JWT (Bearer token) y router /auth."""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo-cambiala")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(nomuser: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": nomuser, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    """Dependencia para proteger endpoints: exige un token Bearer válido."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o ausente",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nomuser = payload.get("sub")
        if not nomuser:
            raise credentials_error
    except jwt.PyJWTError:
        raise credentials_error

    user = db.scalar(select(models.Usuario).where(models.Usuario.nomuser == nomuser))
    if user is None:
        raise credentials_error
    return user


@router.post("/registro", response_model=schemas.UsuarioOut, status_code=201)
def registro(datos: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    nombre_usuario = getattr(datos, "nomuser", None) or getattr(datos, "username")
    nombre_completo = getattr(datos, "nombrecompleto", None) or nombre_usuario

    existe = db.scalar(
        select(models.Usuario).where(models.Usuario.nomuser == nombre_usuario)
    )
    if existe:
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    user = models.Usuario(
        nomuser=nombre_usuario,
        passwd=hash_password(datos.password),
        nombrecompleto=nombre_completo,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.scalar(
        select(models.Usuario).where(models.Usuario.nomuser == form.username)
    )
    if not user or not verify_password(form.password, user.passwd):
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=create_access_token(user.nomuser))
    
