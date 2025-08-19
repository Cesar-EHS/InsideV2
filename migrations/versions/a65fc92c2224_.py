"""empty message

Revision ID: a65fc92c2224
Revises: 33a85b1ecc47, fix_evento_columns, fix_evento_simple
Create Date: 2025-08-15 12:52:26.811535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a65fc92c2224'
down_revision = ('33a85b1ecc47', 'fix_evento_columns', 'fix_evento_simple')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
