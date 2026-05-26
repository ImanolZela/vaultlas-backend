from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    periodo: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


class MovementResponse(BaseModel):
    id: int
    fecha: str
    descripcion: str
    codigo_operacion: Optional[str] = None
    monto: float
    tipo: str
    confirmed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MovementListResponse(BaseModel):
    movements: List[MovementResponse]
    total: int


class ConfirmMovementRequest(BaseModel):
    movement_ids: List[int]


class MonthlyReportResponse(BaseModel):
    mes: int
    ano: int
    total_ingresos: float
    total_egresos: float
    neto: float
    meta_ingresos: Optional[float] = None
    cumplimiento_porcentaje: Optional[float] = None


class HistoricReportResponse(BaseModel):
    reportes: List[MonthlyReportResponse]


class GoalCreate(BaseModel):
    mes: int
    ano: int
    meta_ingresos: float


class GoalResponse(BaseModel):
    id: int
    mes: int
    ano: int
    meta_ingresos: float

    model_config = {"from_attributes": True}
