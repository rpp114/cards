"""empty message

Revision ID: 5872037ebcd6
Revises: 8af07e7b18e1
Create Date: 2018-07-22 11:54:14.555984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5872037ebcd6'
down_revision = '8af07e7b18e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first_login', sa.SMALLINT(), nullable=True))
    op.add_column('user', sa.Column('status', sa.VARCHAR(length=15), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'status')
    op.drop_column('user', 'first_login')
    # ### end Alembic commands ###