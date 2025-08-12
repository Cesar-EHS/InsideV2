"""Add active column to post table

Revision ID: add_active_column
Revises: b74bbd4f8537
Create Date: 2025-08-12 00:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_active_column'
down_revision = 'b74bbd4f8537'
branch_labels = None
depends_on = None


def upgrade():
    # Add active column to post table
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    # Remove active column from post table
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('active')
