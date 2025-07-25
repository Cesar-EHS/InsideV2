"""Eliminar modelo duplicado Curso en crecehs

Revision ID: 87d781030370
Revises: 115b12b5170f
Create Date: 2025-07-04 21:08:49.953766

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87d781030370'
down_revision = '115b12b5170f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categorias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('cursos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categoria_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'categorias', ['categoria_id'], ['id'])
        batch_op.drop_column('categoria')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cursos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categoria', sa.VARCHAR(length=50), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('categoria_id')

    op.drop_table('categorias')
    # ### end Alembic commands ###
