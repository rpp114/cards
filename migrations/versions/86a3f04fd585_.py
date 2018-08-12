"""empty message

Revision ID: 86a3f04fd585
Revises: 6cfd2bc10825
Create Date: 2018-08-12 11:00:24.653226

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '86a3f04fd585'
down_revision = '6cfd2bc10825'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('points_program', 'value')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('points_program', sa.Column('value', mysql.FLOAT(), nullable=True))
    # ### end Alembic commands ###
