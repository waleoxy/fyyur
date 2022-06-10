"""empty message

Revision ID: 407d8e0fc486
Revises: b54408376084
Create Date: 2022-06-09 19:44:22.477124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '407d8e0fc486'
down_revision = 'b54408376084'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
