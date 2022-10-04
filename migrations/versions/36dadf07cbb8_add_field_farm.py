"""add field farm

Revision ID: 36dadf07cbb8
Revises: d583971952eb
Create Date: 2022-09-12 10:36:01.149112

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '36dadf07cbb8'
down_revision = 'd583971952eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('farms', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('farms', sa.Column('area', sa.DECIMAL(precision=10, scale=2), nullable=True))
    op.add_column('farms', sa.Column('code', sa.String(length=255), nullable=True))
    op.drop_column('farms', 'informations')
    op.alter_column('fertilizers', 'type',
               existing_type=sa.VARCHAR(length=255),
               comment='Hữu cơ/Vô cơ/Khác',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('fertilizers', 'type',
               existing_type=sa.VARCHAR(length=255),
               comment=None,
               existing_comment='Hữu cơ/Vô cơ/Khác',
               existing_nullable=True)
    op.add_column('farms', sa.Column('informations', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.drop_column('farms', 'code')
    op.drop_column('farms', 'area')
    op.drop_column('farms', 'description')
    # ### end Alembic commands ###
