"""empty message

Revision ID: 72b3eca48562
Revises: 5872037ebcd6
Create Date: 2018-07-25 20:37:40.501027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72b3eca48562'
down_revision = '5872037ebcd6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('spending_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('card_category_lookup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('company_name', sa.VARCHAR(length=255), nullable=True),
    sa.Column('earning_percent', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['spending_category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('card_category_lookup')
    op.drop_table('spending_category')
    # ### end Alembic commands ###
