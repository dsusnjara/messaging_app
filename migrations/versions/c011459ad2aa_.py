"""empty message

Revision ID: c011459ad2aa
Revises: 5bfc6a85727b
Create Date: 2020-03-07 19:18:10.779187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c011459ad2aa'
down_revision = '5bfc6a85727b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message') as batch_op:
        batch_op.drop_column('message')
        batch_op.add_column(sa.Column('body', sa.TEXT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message') as batch_op:
        batch_op.drop_column('body')
        batch_op.add_column(sa.Column('message', sa.TEXT(), nullable=True))
    # ### end Alembic commands ###