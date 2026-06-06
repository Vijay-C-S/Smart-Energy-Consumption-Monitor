"""add daily_kwh_threshold to households

Revision ID: 0002_add_household_threshold
Revises: 0001_initial
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa

revision = '0002_add_household_threshold'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'households',
        sa.Column('daily_kwh_threshold', sa.Float(), nullable=False, server_default='20.0'),
    )


def downgrade():
    op.drop_column('households', 'daily_kwh_threshold')
