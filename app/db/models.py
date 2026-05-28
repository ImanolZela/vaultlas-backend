from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, UniqueConstraint, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    documents = relationship("Document", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    incomes = relationship("Income", back_populates="user")
    expenses = relationship("Expense", back_populates="user")
    fixed_expenses = relationship("ExpenseFixedMonthly", back_populates="user")
    budgets = relationship("MonthlyBudget", back_populates="user")
    pdf_movements = relationship("PdfMovement", back_populates="user")
    reconciliation_reports = relationship("ReconciliationReport", back_populates="user")
    reconciliation_items = relationship("ReconciliationItem", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pdf_hash = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    bank = Column(String, default="BCP")
    status = Column(String, default="pending")
    periodo = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="documents")
    movements = relationship("Movement", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("pdf_hash", "user_id", name="uq_pdf_hash_user"),)


class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    fecha = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    codigo_operacion = Column(String)
    monto = Column(Float, nullable=False)
    tipo = Column(String, nullable=False)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="movements")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mes = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    meta_ingresos = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="goals")

    __table_args__ = (UniqueConstraint("user_id", "mes", "ano", name="uq_user_mes_ano"),)


class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurring_day = Column(Integer)
    recurring_month_from = Column(Date)
    recurring_month_to = Column(Date)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="incomes")


class Expense(Base):
    __tablename__ = "expense"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    bucket = Column(String, nullable=False)
    category_name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    payment_method = Column(String(50))
    receipt_image_url = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="expenses")


class ExpenseFixedMonthly(Base):
    __tablename__ = "expense_fixed_monthly"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category_name = Column(String(100), nullable=False)
    bucket = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    day_of_month = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="fixed_expenses")


class MonthlyBudget(Base):
    __tablename__ = "monthly_budget"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    month = Column(Date, nullable=False)

    total_income = Column(Float, default=0)
    needs_percent = Column(Float, default=50.0)
    wants_percent = Column(Float, default=30.0)
    savings_percent = Column(Float, default=20.0)
    debt_amount = Column(Float, default=0)

    budgeted_needs = Column(Float, default=0)
    budgeted_wants = Column(Float, default=0)
    budgeted_savings = Column(Float, default=0)

    actual_needs = Column(Float, default=0)
    actual_wants = Column(Float, default=0)
    actual_savings = Column(Float, default=0)
    actual_debt = Column(Float, default=0)

    status = Column(String(20), default="draft")
    pdf_received_date = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="budgets")
    __table_args__ = (UniqueConstraint("user_id", "month", name="uq_user_budget_month"),)


class PdfMovement(Base):
    __tablename__ = "pdf_movement"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    balance = Column(Float)
    operation_code = Column(String(50))
    is_debit = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="pdf_movements")


class ReconciliationReport(Base):
    __tablename__ = "reconciliation_report"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    month = Column(Date, nullable=False)
    status = Column(String(20), default="pending")
    total_unmatched = Column(Integer, default=0)
    total_categorized = Column(Integer, default=0)
    income_difference = Column(Float, default=0)
    expense_difference = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="reconciliation_reports")
    items = relationship("ReconciliationItem", back_populates="report", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("user_id", "month", name="uq_reconciliation_month"),)


class ReconciliationItem(Base):
    __tablename__ = "reconciliation_item"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reconciliation_report.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pdf_date = Column(Date, nullable=False)
    pdf_description = Column(String(500), nullable=False)
    pdf_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    suggested_bucket = Column(String(20))
    user_bucket = Column(String(20))
    user_category = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reconciliation_items")
    report = relationship("ReconciliationReport", back_populates="items")
