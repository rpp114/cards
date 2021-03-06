"""empty message

Revision ID: e23da2ef95d6
Revises: a07f76b045c5
Create Date: 2018-08-23 20:57:17.958562

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e23da2ef95d6'
down_revision = 'a07f76b045c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reward_program',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_name', sa.VARCHAR(length=100), nullable=True),
    sa.Column('program_name', sa.VARCHAR(length=100), nullable=True),
    sa.Column('company_name', sa.VARCHAR(length=100), nullable=True),
    sa.Column('redeem_value', sa.Float(), nullable=True),
    sa.Column('active', sa.BOOLEAN(), nullable=True),
    sa.Column('ulu', sa.VARCHAR(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('program_name')
    )
    op.create_table('reward_program_lookup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('points_program_id', sa.Integer(), nullable=True),
    sa.Column('reward_program_id', sa.Integer(), nullable=True),
    sa.Column('active', sa.BOOLEAN(), nullable=True),
    sa.Column('ulu', sa.VARCHAR(length=50), nullable=True),
    sa.ForeignKeyConstraint(['points_program_id'], ['points_program.id'], ),
    sa.ForeignKeyConstraint(['reward_program_id'], ['reward_program.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('reward_category')
    op.drop_table('reward_category_lookup')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reward_category_lookup',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('reward_category_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('company_name', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('redeem_value', mysql.FLOAT(), nullable=True),
    sa.Column('active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('points_program_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('ulu', mysql.VARCHAR(length=50), nullable=True),
    sa.ForeignKeyConstraint(['points_program_id'], ['points_program.id'], name='reward_category_lookup_ibfk_3'),
    sa.ForeignKeyConstraint(['reward_category_id'], ['reward_category.id'], name='reward_category_lookup_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('reward_category',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=256), nullable=True),
    sa.Column('active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('ulu', mysql.VARCHAR(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_index('name', 'reward_category', ['name'], unique=True)
    op.drop_table('reward_program_lookup')
    op.drop_table('reward_program')
    # ### end Alembic commands ###
