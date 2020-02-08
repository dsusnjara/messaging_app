"""empty message

Revision ID: 2c295f978e7d
Revises: 95fa99a1c690
Create Date: 2020-02-07 01:27:36.522995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c295f978e7d'
down_revision = '95fa99a1c690'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_message_timestamp'), 'message', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_message_timestamp'), table_name='message')
    op.drop_column('message', 'timestamp')
    # ### end Alembic commands ###
