"""add income expense budget reconciliation tables

Revision ID: a1b2c3d4e5f6
Revises: 001_initial
Create Date: 2026-05-28

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'income',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('description', sa.String(200), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), default=False),
        sa.Column('recurring_day', sa.Integer()),
        sa.Column('recurring_month_from', sa.Date()),
        sa.Column('recurring_month_to', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_table(
        'expense',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('bucket', sa.String(), nullable=False),
        sa.Column('category_name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(200), nullable=False),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('receipt_image_url', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_table(
        'expense_fixed_monthly',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category_name', sa.String(100), nullable=False),
        sa.Column('bucket', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('day_of_month', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_table(
        'monthly_budget',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('total_income', sa.Float(), default=0),
        sa.Column('needs_percent', sa.Float(), default=50.0),
        sa.Column('wants_percent', sa.Float(), default=30.0),
        sa.Column('savings_percent', sa.Float(), default=20.0),
        sa.Column('debt_amount', sa.Float(), default=0),
        sa.Column('budgeted_needs', sa.Float(), default=0),
        sa.Column('budgeted_wants', sa.Float(), default=0),
        sa.Column('budgeted_savings', sa.Float(), default=0),
        sa.Column('actual_needs', sa.Float(), default=0),
        sa.Column('actual_wants', sa.Float(), default=0),
        sa.Column('actual_savings', sa.Float(), default=0),
        sa.Column('actual_debt', sa.Float(), default=0),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('pdf_received_date', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('user_id', 'month', name='uq_user_budget_month'),
    )
    op.create_table(
        'pdf_movement',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('balance', sa.Float()),
        sa.Column('operation_code', sa.String(50)),
        sa.Column('is_debit', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )
    op.create_table(
        'reconciliation_report',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('total_unmatched', sa.Integer(), default=0),
        sa.Column('total_categorized', sa.Integer(), default=0),
        sa.Column('income_difference', sa.Float(), default=0),
        sa.Column('expense_difference', sa.Float(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('user_id', 'month', name='uq_reconciliation_month'),
    )
    op.create_table(
        'reconciliation_item',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('report_id', sa.Integer(), sa.ForeignKey('reconciliation_report.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('pdf_date', sa.Date(), nullable=False),
        sa.Column('pdf_description', sa.String(500), nullable=False),
        sa.Column('pdf_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('suggested_bucket', sa.String(20)),
        sa.Column('user_bucket', sa.String(20)),
        sa.Column('user_category', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )


def downgrade():
    op.drop_table('reconciliation_item')
    op.drop_table('reconciliation_report')
    op.drop_table('pdf_movement')
    op.drop_table('monthly_budget')
    op.drop_table('expense_fixed_monthly')
    op.drop_table('expense')
    op.drop_table('income')
