"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-06-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'households',
        sa.Column('household_id', sa.Integer(), primary_key=True),
        sa.Column('customer_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'smart_meters',
        sa.Column('meter_id', sa.Integer(), primary_key=True),
        sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.household_id', ondelete='SET NULL'), nullable=True),
        sa.Column('meter_number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'ACTIVE'"), nullable=False),
        sa.Column('installed_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'meter_readings',
        sa.Column('reading_id', sa.Integer(), primary_key=True),
        sa.Column('meter_id', sa.Integer(), sa.ForeignKey('smart_meters.meter_id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('energy_consumed_kwh', sa.Float(), nullable=False),
        sa.Column('voltage', sa.Float(), nullable=True),
        sa.Column('current', sa.Float(), nullable=True),
        sa.Column('power_factor', sa.Float(), nullable=True),
    )

    op.create_table(
        'alerts',
        sa.Column('alert_id', sa.Integer(), primary_key=True),
        sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.household_id', ondelete='SET NULL'), nullable=True),
        sa.Column('meter_id', sa.Integer(), sa.ForeignKey('smart_meters.meter_id', ondelete='SET NULL'), nullable=True),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'OPEN'"), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'tariff_config',
        sa.Column('tariff_id', sa.Integer(), primary_key=True),
        sa.Column('rate_per_kwh', sa.Float(), nullable=False),
        sa.Column('effective_from', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )


def downgrade():
    op.drop_table('tariff_config')
    op.drop_table('alerts')
    op.drop_table('meter_readings')
    op.drop_table('smart_meters')
    op.drop_table('households')
