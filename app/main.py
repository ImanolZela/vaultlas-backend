from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.api.routes.movements import router as movements_router
from app.api.routes.reports import router as reports_router
from app.api.routes.goals import router as goals_router
from app.api.routes import exports
from app.api.routes.income import router as income_router
from app.api.routes.expense import router as expense_router
from app.api.routes.budget import router as budget_router
from app.api.routes.reconciliation import router as reconciliation_router
from app.api.routes.annual_summary import router as annual_router

def run_migrations():
    from alembic.config import Config
    from alembic import command
    import os
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", redirect_slashes=False)


@app.on_event("startup")
async def on_startup():
    try:
        run_migrations()
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").warning(f"Migration skipped: {e}")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(movements_router)
app.include_router(reports_router)
app.include_router(goals_router)
app.include_router(exports.router, prefix="/api/exports", tags=["exports"])
app.include_router(income_router)
app.include_router(expense_router)
app.include_router(budget_router)
app.include_router(reconciliation_router)
app.include_router(annual_router)


@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} API"}


@app.get("/health")
def health():
    return {"status": "ok"}
