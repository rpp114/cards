"""empty message

Revision ID: 45405ee75e48
Revises: 
Create Date: 2018-07-26 21:03:44.713312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45405ee75e48'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('points_program',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=256), nullable=True),
    sa.Column('value', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('reward_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('spending_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=256), nullable=True),
    sa.Column('email', sa.VARCHAR(length=256), nullable=True),
    sa.Column('password', sa.VARCHAR(length=256), nullable=True),
    sa.Column('session_token', sa.VARCHAR(length=256), nullable=True),
    sa.Column('status', sa.VARCHAR(length=15), nullable=True),
    sa.Column('first_login', sa.SMALLINT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('card',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('points_program_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.VARCHAR(length=256), nullable=True),
    sa.Column('card_type', sa.VARCHAR(length=15), nullable=True),
    sa.Column('apply_link_url', sa.TEXT(), nullable=True),
    sa.Column('image_link_url', sa.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['points_program_id'], ['points_program.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reward_category_lookup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_id', sa.Integer(), nullable=True),
    sa.Column('reward_category_id', sa.Integer(), nullable=True),
    sa.Column('company_name', sa.VARCHAR(length=255), nullable=True),
    sa.Column('redeem_value', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
    sa.ForeignKeyConstraint(['reward_category_id'], ['reward_category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('signup_bonus',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_id', sa.Integer(), nullable=True),
    sa.Column('days_for_spend', sa.Integer(), nullable=True),
    sa.Column('minimum_spend', sa.Integer(), nullable=True),
    sa.Column('annual_fee', sa.Integer(), nullable=True),
    sa.Column('annual_fee_waived', sa.VARCHAR(length=10), nullable=True),
    sa.Column('bonus_points', sa.Integer(), nullable=True),
    sa.Column('from_date', sa.DATETIME(), nullable=True),
    sa.Column('to_date', sa.DATETIME(), nullable=True),
    sa.Column('status', sa.VARCHAR(length=15), nullable=True),
    sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spending_category_lookup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_id', sa.Integer(), nullable=True),
    sa.Column('spending_category_id', sa.Integer(), nullable=True),
    sa.Column('company_name', sa.VARCHAR(length=255), nullable=True),
    sa.Column('earning_percent', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
    sa.ForeignKeyConstraint(['spending_category_id'], ['spending_category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_card_lookup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('card_id', sa.Integer(), nullable=True),
    sa.Column('active_date', sa.DATETIME(), nullable=True),
    sa.Column('cancel_date', sa.DATETIME(), nullable=True),
    sa.Column('status', sa.VARCHAR(length=15), nullable=True),
    sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_card_lookup')
    op.drop_table('spending_category_lookup')
    op.drop_table('signup_bonus')
    op.drop_table('reward_category_lookup')
    op.drop_table('card')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('spending_category')
    op.drop_table('reward_category')
    op.drop_table('points_program')
    op.drop_table('company')
    # ### end Alembic commands ###
