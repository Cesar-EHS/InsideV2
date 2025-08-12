"""Add missing columns to evento table

Revision ID: fix_evento_columns
Revises: add_active_column
Create Date: 2025-08-12 00:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_evento_columns'
down_revision = 'add_active_column'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to evento table
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('max_attendees', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_recurring', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('recurrence_pattern', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('reminder_sent', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=False, server_default='1'))
        batch_op.create_foreign_key('fk_evento_created_by', 'usuarios', ['created_by'], ['id'])

    # Create event_attendees table only if it doesn't exist
    # Check if table exists by trying to get its info
    from sqlalchemy import inspect
    inspector = inspect(op.get_bind())
    if 'event_attendees' not in inspector.get_table_names():
        op.create_table('event_attendees',
            sa.Column('event_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('registered_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['event_id'], ['evento.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['usuarios.id'], ),
            sa.PrimaryKeyConstraint('event_id', 'user_id')
        )


def downgrade():
    # Drop event_attendees table
    op.drop_table('event_attendees')
    
    # Remove columns from evento table
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.drop_constraint('fk_evento_created_by', type_='foreignkey')
        batch_op.drop_column('active')
        batch_op.drop_column('created_by')
        batch_op.drop_column('reminder_sent')
        batch_op.drop_column('recurrence_pattern')
        batch_op.drop_column('is_recurring')
        batch_op.drop_column('max_attendees')
        batch_op.drop_column('type')
        batch_op.drop_column('location')
