"""init

Revision ID: 69e1703dd4a2
Revises: 
Create Date: 2022-09-07 08:01:24.350278

"""
from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy

# revision identifiers, used by Alembic.
revision = '69e1703dd4a2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('resource',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('file_size', sa.DECIMAL(precision=2), nullable=True),
    sa.Column('file_path', sa.String(length=255), nullable=True),
    sa.Column('file_type', sa.String(length=255), nullable=True),
    sa.Column('updated_by', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('role',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('key', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('updated_by', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_table('users',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('role_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('dob', sa.DateTime(timezone=True), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('created_by', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('updated_by', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('avatar_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.ForeignKeyConstraint(['avatar_id'], ['resource.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),    
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),    
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('role')
    op.drop_table('resource')
    # ### end Alembic commands ###