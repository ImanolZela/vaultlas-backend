# Vaultlas Backend

Backend de Vaultlas — plataforma de gestión financiera personal. Procesa estados de cuenta bancarios (BCP Perú) en PDF, extrae movimientos y genera reportes.

## Stack

- **FastAPI** — API REST
- **Celery + Redis** — Procesamiento asíncrono de PDFs
- **PostgreSQL + Alembic** — Base de datos y migraciones
- **pdfplumber + pypdf** — Extracción de datos de PDFs

## Inicio rápido (desarrollo local)

```bash
cp .env.example .env
docker compose up --build
```

API disponible en: http://localhost:8000  
Documentación: http://localhost:8000/docs

## Despliegue (Dokploy)

Conectar este repositorio en Dokploy. Usará el `Dockerfile` de la raíz.
