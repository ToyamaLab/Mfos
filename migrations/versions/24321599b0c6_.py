"""empty message

Revision ID: 24321599b0c6
Revises: a82eac4e419c
Create Date: 2020-12-17 17:00:12.934945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24321599b0c6'
down_revision = 'a82eac4e419c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'schedule', ['event_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'schedule', type_='unique')
    # ### end Alembic commands ###
