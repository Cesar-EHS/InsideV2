"""Unir migraciones

Revision ID: bf83eaf69fdf
Revises: a65fc92c2224, add_descripcion_field
Create Date: 2025-08-25 12:16:49.875295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf83eaf69fdf'
down_revision = ('a65fc92c2224', 'add_descripcion_field')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
