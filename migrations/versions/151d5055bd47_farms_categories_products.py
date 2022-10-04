"""farms_categories_products

Revision ID: 151d5055bd47
Revises: 69e1703dd4a2
Create Date: 2022-09-08 08:12:35.947205

"""
from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy

# revision identifiers, used by Alembic.
revision = '151d5055bd47'
down_revision = '69e1703dd4a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('updated_by', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),   
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('farms',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('informations', sa.PickleType(), nullable=True),
    sa.Column('updated_by', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),   
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('products',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('category_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('farm_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('code', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('updated_by', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),   
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ),
    sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('products')
    op.drop_table('farms')
    op.drop_table('categories')
    # ### end Alembic commands ###