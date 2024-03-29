"""empty message

Revision ID: 6de89519d295
Revises: 7cd9a638b9c1
Create Date: 2024-01-07 20:23:40.963698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6de89519d295'
down_revision = '7cd9a638b9c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('urls', schema=None) as batch_op:
        batch_op.add_column(sa.Column('visits', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('urls', schema=None) as batch_op:
        batch_op.drop_column('visits')

    # ### end Alembic commands ###
