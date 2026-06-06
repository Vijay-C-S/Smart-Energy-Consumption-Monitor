"""enforce one meter per household

Revision ID: 0003_one_meter_per_household
Revises: 0002_add_household_threshold
Create Date: 2026-06-04
"""
from alembic import op

revision = '0003_one_meter_per_household'
down_revision = '0002_add_household_threshold'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        'uq_smart_meters_household_id',
        'smart_meters',
        ['household_id'],
    )


def downgrade():
    op.drop_constraint(
        'uq_smart_meters_household_id',
        'smart_meters',
        type_='unique',
    )
