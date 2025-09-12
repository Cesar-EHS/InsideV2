"""Agregar campo descripcion a tabla documentos

Revision ID: add_descripcion_field
Revises: 252fc144b630
Create Date: 2025-07-20 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_descripcion_field'
down_revision = '252fc144b630'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar campo descripcion a la tabla documentos
    with op.batch_alter_table('documentos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('descripcion', sa.Text(), nullable=True))


def downgrade():
    # Eliminar campo descripcion de la tabla documentos
    with op.batch_alter_table('documentos', schema=None) as batch_op:
        batch_op.drop_column('descripcion')
