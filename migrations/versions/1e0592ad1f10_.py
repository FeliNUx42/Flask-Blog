"""empty message

Revision ID: 1e0592ad1f10
Revises: 
Create Date: 2021-08-24 17:04:48.774616

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e0592ad1f10'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('fcreated', sa.DateTime(timezone=True), nullable=True))
    op.drop_column('user', 'created')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('created', sa.DATETIME(), nullable=True))
    op.drop_column('user', 'fcreated')
    # ### end Alembic commands ###