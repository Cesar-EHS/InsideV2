"""
Revision ID: add_imagen_to_cursos
Revises: 
Create Date: 2025-07-04
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_imagen_to_cursos'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('cursos', sa.Column('imagen', sa.String(length=255), nullable=True))

def downgrade():
    op.drop_column('cursos', 'imagen')
