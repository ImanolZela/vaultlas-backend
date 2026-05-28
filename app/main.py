from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.api.routes.movements import router as movements_router
from app.api.routes.reports import router as reports_router
from app.api.routes.goals import router as goals_router
from app.api.routes import exports

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", redirect_slashes=False)

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


@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} API"}


@app.get("/health")
def health():
    return {"status": "ok"}
