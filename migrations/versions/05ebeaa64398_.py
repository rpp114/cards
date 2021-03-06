"""empty message

Revision ID: 05ebeaa64398
Revises: 86a3f04fd585
Create Date: 2018-08-13 20:17:21.915327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05ebeaa64398'
down_revision = '86a3f04fd585'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card', sa.Column('ulu', sa.VARCHAR(length=50), nullable=True))
    op.add_column('company', sa.Column('ulu', sa.VARCHAR(length=50), nullable=True))
    op.add_column('points_program', sa.Column('ulu', sa.VARCHAR(length=50), nullable=True))
    op.add_column('reward_category', sa.Column('ulu', sa.VARCHAR(length=50), nullable=True))
    op.add_column('reward_category_lookup', sa.Column('ulu', sa.VARCHAR(length=50), nullable=True))
    op.add_column('signup_bonus', sa.Column('ulu', sa.VARCHAR(length=50), nullable=True))
    op.add_column('spending_category', sa.Column('ulu', sa.VARCHAR(length=50), nullable=True))
    op.add_column('spending_category_lookup', sa.Column('ulu', sa.VARCHAR(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('spending_category_lookup', 'ulu')
    op.drop_column('spending_category', 'ulu')
    op.drop_column('signup_bonus', 'ulu')
    op.drop_column('reward_category_lookup', 'ulu')
    op.drop_column('reward_category', 'ulu')
    op.drop_column('points_program', 'ulu')
    op.drop_column('company', 'ulu')
    op.drop_column('card', 'ulu')
    # ### end Alembic commands ###
