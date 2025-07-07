"""Unificar heads de migración

Revision ID: 3873e878476f
Revises: add_imagen_to_cursos, baf8fee885a3
Create Date: 2025-07-04 19:29:53.919544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3873e878476f'
down_revision = ('add_imagen_to_cursos', 'baf8fee885a3')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
