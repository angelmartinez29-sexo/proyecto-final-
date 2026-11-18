# API Librería Chiapas

API REST con FastAPI + PostgreSQL (SQLAlchemy) + Pydantic.

## Puesta en marcha

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # y ajusta DATABASE_URL / SECRET_KEY
createdb libreria_chiapas       # o créala desde pgAdmin
uvicorn app.main:app --reload
```

Documentación interactiva: http://127.0.0.1:8000/docs

## Flujo de uso

1. `POST /auth/registro` → crea un usuario (`username`, `password`).
2. `POST /auth/login` (form-data) → devuelve `access_token`.
3. En `/docs` pulsa **Authorize** y pega el token, o envía el header
   `Authorization: Bearer <token>`.

## Endpoints

| Método | Ruta | Auth |
|---|---|---|
| GET | `/libros/` (filtros: titulo, autor, editorial_id, skip, limit) | No |
| GET | `/libros/{id}` | No |
| POST / PUT / DELETE | `/libros/` · `/libros/{id}` | Sí |
| GET | `/editoriales/` · `/editoriales/{id}` · `/editoriales/{id}/libros` | No |
| POST / PUT / DELETE | `/editoriales/` · `/editoriales/{id}` | Sí |
