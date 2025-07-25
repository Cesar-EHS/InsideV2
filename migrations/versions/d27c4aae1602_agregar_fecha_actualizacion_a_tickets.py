"""Agregar fecha_actualizacion a tickets

Revision ID: d27c4aae1602
Revises: add_descripcion_field
Create Date: 2025-07-22 16:02:56.260864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd27c4aae1602'
down_revision = 'add_descripcion_field'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cursos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categoria_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_cursos_categoria_id', 'categorias', ['categoria_id'], ['id'])
        batch_op.drop_column('categoria')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('visible_para_todos',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('1'))

    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.drop_column('fecha_actualizacion')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('visible_para_todos',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('1'))

    with op.batch_alter_table('cursos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categoria', sa.VARCHAR(length=50), nullable=False))
        batch_op.drop_constraint('fk_cursos_categoria_id', type_='foreignkey')
        batch_op.drop_column('categoria_id')

    # ### end Alembic commands ###
