"""empty message

Revision ID: 8af07e7b18e1
Revises: f175bc08d9c1
Create Date: 2018-07-07 08:20:12.877622

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8af07e7b18e1'
down_revision = 'f175bc08d9c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'points_program', ['name'])
    op.drop_constraint('points_program_ibfk_1', 'points_program', type_='foreignkey')
    op.drop_column('points_program', 'reward_id')
    op.add_column('reward', sa.Column('points_program_id', sa.Integer(), nullable=True))
    op.drop_index('name', table_name='reward')
    op.create_foreign_key(None, 'reward', 'points_program', ['points_program_id'], ['id'])
    op.drop_column('reward', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reward', sa.Column('name', mysql.VARCHAR(length=256), nullable=True))
    op.drop_constraint(None, 'reward', type_='foreignkey')
    op.create_index('name', 'reward', ['name'], unique=True)
    op.drop_column('reward', 'points_program_id')
    op.add_column('points_program', sa.Column('reward_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('points_program_ibfk_1', 'points_program', 'reward', ['reward_id'], ['id'])
    op.drop_constraint(None, 'points_program', type_='unique')
    # ### end Alembic commands ###
