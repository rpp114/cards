"""empty message

Revision ID: 6cfd2bc10825
Revises: c8cb8db4e1ed
Create Date: 2018-08-09 08:43:29.362562

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6cfd2bc10825'
down_revision = 'c8cb8db4e1ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card', sa.Column('active', sa.BOOLEAN(), nullable=True))
    op.add_column('card', sa.Column('terms_link_url', sa.TEXT(), nullable=True))
    op.add_column('company', sa.Column('active', sa.BOOLEAN(), nullable=True))
    op.add_column('points_program', sa.Column('active', sa.BOOLEAN(), nullable=True))
    op.add_column('reward_category', sa.Column('active', sa.BOOLEAN(), nullable=True))
    op.add_column('reward_category_lookup', sa.Column('active', sa.BOOLEAN(), nullable=True))
    op.add_column('reward_category_lookup', sa.Column('points_program_id', sa.Integer(), nullable=True))
    op.drop_constraint('reward_category_lookup_ibfk_1', 'reward_category_lookup', type_='foreignkey')
    op.create_foreign_key(None, 'reward_category_lookup', 'points_program', ['points_program_id'], ['id'])
    op.drop_column('reward_category_lookup', 'card_id')
    op.add_column('spending_category', sa.Column('active', sa.BOOLEAN(), nullable=True))
    op.add_column('spending_category_lookup', sa.Column('active', sa.BOOLEAN(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('spending_category_lookup', 'active')
    op.drop_column('spending_category', 'active')
    op.add_column('reward_category_lookup', sa.Column('card_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'reward_category_lookup', type_='foreignkey')
    op.create_foreign_key('reward_category_lookup_ibfk_1', 'reward_category_lookup', 'card', ['card_id'], ['id'])
    op.drop_column('reward_category_lookup', 'points_program_id')
    op.drop_column('reward_category_lookup', 'active')
    op.drop_column('reward_category', 'active')
    op.drop_column('points_program', 'active')
    op.drop_column('company', 'active')
    op.drop_column('card', 'terms_link_url')
    op.drop_column('card', 'active')
    # ### end Alembic commands ###
