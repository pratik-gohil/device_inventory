"""initial migration

Revision ID: cf5a82d2eda4
Revises: 
Create Date: 2021-05-23 17:43:46.041343

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cf5a82d2eda4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin', sa.Column('email', sa.String(length=255), nullable=False))
    op.drop_index('date_added', table_name='admin')
    op.create_unique_constraint(None, 'admin', ['email'])
    op.drop_column('admin', 'date_added')
    op.add_column('devices', sa.Column('type', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('devices', 'type')
    op.add_column('admin', sa.Column('date_added', mysql.VARCHAR(length=255), nullable=False))
    op.drop_constraint(None, 'admin', type_='unique')
    op.create_index('date_added', 'admin', ['date_added'], unique=False)
    op.drop_column('admin', 'email')
    # ### end Alembic commands ###