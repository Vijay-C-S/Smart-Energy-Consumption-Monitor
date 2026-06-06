"""add password_hash to households

Revision ID: 0004_add_password_hash
Revises: 0003_one_meter_per_household
Create Date: 2026-06-04
"""
from alembic import op
import sqlalchemy as sa

revision = '0004_add_password_hash'
down_revision = '0003_one_meter_per_household'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('households', sa.Column('password_hash', sa.String(200), nullable=True))


def downgrade():
    op.drop_column('households', 'password_hash')
