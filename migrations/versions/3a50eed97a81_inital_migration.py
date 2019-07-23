"""inital migration

Revision ID: 3a50eed97a81
Revises: 
Create Date: 2019-07-22 20:25:49.973289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a50eed97a81'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('predictions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('response_time', sa.DateTime(), nullable=True),
    sa.Column('recorded_time', sa.DateTime(), nullable=True),
    sa.Column('line_ref', sa.String(), nullable=True),
    sa.Column('direction_ref', sa.String(), nullable=True),
    sa.Column('stop_point_ref', sa.Integer(), nullable=True),
    sa.Column('scheduled_arrival_time', sa.DateTime(), nullable=True),
    sa.Column('expected_arrival_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('predictions')
    # ### end Alembic commands ###
