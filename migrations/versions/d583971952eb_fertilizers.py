"""fertilizers

Revision ID: d583971952eb
Revises: 45a4220117ab
Create Date: 2022-09-10 12:37:48.610239

"""
from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy 


# revision identifiers, used by Alembic.
revision = 'd583971952eb'
down_revision = '45a4220117ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('fertilizers',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('manufacturer', sa.String(length=255), nullable=True),
    sa.Column('manufacture_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('compositions', sa.String(length=255), nullable=True),
    sa.Column('code', sa.String(length=255), nullable=True),
    sa.Column('type', sa.String(length=255), nullable=True),
    sa.Column('updated_by', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),    
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('fertilizers')
