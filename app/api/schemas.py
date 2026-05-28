from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


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


# ─── INCOME ───────────────────────────────────────────────────
class IncomeCreate(BaseModel):
    date: date
    type: str
    description: str
    amount: float
    is_recurring: bool = False
    recurring_day: Optional[int] = None
    recurring_month_from: Optional[date] = None
    recurring_month_to: Optional[date] = None


class IncomeUpdate(BaseModel):
    date: Optional[date] = None
    type: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    is_recurring: Optional[bool] = None
    recurring_day: Optional[int] = None
    recurring_month_from: Optional[date] = None
    recurring_month_to: Optional[date] = None


class IncomeResponse(BaseModel):
    id: int
    user_id: int
    date: date
    type: str
    description: str
    amount: float
    is_recurring: bool
    recurring_day: Optional[int] = None
    recurring_month_from: Optional[date] = None
    recurring_month_to: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── EXPENSE ──────────────────────────────────────────────────
class ExpenseCreate(BaseModel):
    date: date
    amount: float
    bucket: str
    category_name: str
    description: str
    payment_method: Optional[str] = None
    receipt_image_url: Optional[str] = None


class ExpenseUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[float] = None
    bucket: Optional[str] = None
    category_name: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    receipt_image_url: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    date: date
    amount: float
    bucket: str
    category_name: str
    description: str
    payment_method: Optional[str] = None
    receipt_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpenseFixedMonthlyCreate(BaseModel):
    name: str
    category_name: str
    bucket: str
    amount: float
    day_of_month: int
    is_active: bool = True
    start_date: date
    end_date: Optional[date] = None


class ExpenseFixedMonthlyResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category_name: str
    bucket: str
    amount: float
    day_of_month: int
    is_active: bool
    start_date: date
    end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── MONTHLY BUDGET ───────────────────────────────────────────
class MonthlyBudgetCreate(BaseModel):
    month: date
    needs_percent: float = 50.0
    wants_percent: float = 30.0
    savings_percent: float = 20.0
    debt_amount: float = 0


class MonthlyBudgetUpdate(BaseModel):
    needs_percent: Optional[float] = None
    wants_percent: Optional[float] = None
    savings_percent: Optional[float] = None
    debt_amount: Optional[float] = None


class MonthlyBudgetResponse(BaseModel):
    id: int
    user_id: int
    month: date
    total_income: float
    needs_percent: float
    wants_percent: float
    savings_percent: float
    debt_amount: float
    budgeted_needs: float
    budgeted_wants: float
    budgeted_savings: float
    actual_needs: float
    actual_wants: float
    actual_savings: float
    actual_debt: float
    status: str
    pdf_received_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── RECONCILIATION ───────────────────────────────────────────
class ReconciliationItemUpdate(BaseModel):
    status: Optional[str] = None
    user_bucket: Optional[str] = None
    user_category: Optional[str] = None


class ReconciliationItemResponse(BaseModel):
    id: int
    report_id: int
    pdf_date: date
    pdf_description: str
    pdf_amount: float
    status: str
    suggested_bucket: Optional[str] = None
    user_bucket: Optional[str] = None
    user_category: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReconciliationReportResponse(BaseModel):
    id: int
    month: date
    status: str
    total_unmatched: int
    total_categorized: int
    income_difference: float
    expense_difference: float
    items: List[ReconciliationItemResponse]
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
