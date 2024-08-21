"""Initial migration

Revision ID: 6d69b9a78691
Revises: c4c2d481d332
Create Date: 2024-08-21 16:32:09.035630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '6d69b9a78691'
down_revision: Union[str, None] = 'c4c2d481d332'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('employee_onboarding')
    op.drop_index('employee_email', table_name='employee_employment_details')
    op.drop_table('employee_employment_details')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employee_employment_details',
    sa.Column('employment_id', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('employee_email', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('job_position', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('department', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('start_date', sa.DATE(), nullable=False),
    sa.Column('employment_type', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('reporting_manager', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('work_location', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('basic_salary', mysql.DECIMAL(precision=10, scale=2), nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('releave_date', sa.DATE(), nullable=True),
    sa.Column('employee_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employee_onboarding.id'], name='employee_employment_details_ibfk_1'),
    sa.PrimaryKeyConstraint('employment_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('employee_email', 'employee_employment_details', ['employee_email'], unique=True)
    op.create_table('employee_onboarding',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('firstname', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('lastname', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('dateofbirth', sa.DATE(), nullable=False),
    sa.Column('contactnumber', mysql.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('emailaddress', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('address', mysql.TEXT(), nullable=False),
    sa.Column('nationality', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('gender', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('maritalstatus', mysql.VARCHAR(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
