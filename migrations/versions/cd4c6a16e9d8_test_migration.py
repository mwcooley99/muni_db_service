"""test migration

Revision ID: cd4c6a16e9d8
Revises: 3a50eed97a81
Create Date: 2019-07-22 20:29:10.571126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd4c6a16e9d8'
down_revision = '3a50eed97a81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('predictions', sa.Column('thing', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('predictions', 'thing')
    # ### end Alembic commands ###