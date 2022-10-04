"""column updated at

Revision ID: 45a4220117ab
Revises: 301e9d3187db
Create Date: 2022-09-10 12:30:52.296931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45a4220117ab'
down_revision = '301e9d3187db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('resource', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('role', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))


def downgrade() -> None:
    op.drop_column("resource", "updated_at")
    op.drop_column("role", "updated_at")
