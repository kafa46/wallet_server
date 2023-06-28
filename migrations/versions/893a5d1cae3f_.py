"""empty message

Revision ID: 893a5d1cae3f
Revises: 64d5bbe40aa6
Create Date: 2023-06-11 06:06:35.936921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '893a5d1cae3f'
down_revision = '64d5bbe40aa6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('block_chain')
    op.drop_table('transaction')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('block_id', sa.INTEGER(), nullable=True),
    sa.Column('send_addr', sa.VARCHAR(length=300), nullable=True),
    sa.Column('recv_addr', sa.VARCHAR(length=300), nullable=True),
    sa.Column('amount', sa.FLOAT(), nullable=True),
    sa.Column('create_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['block_id'], ['block_chain.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('block_chain',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('prev_hash', sa.VARCHAR(length=300), nullable=True),
    sa.Column('nonce', sa.INTEGER(), nullable=True),
    sa.Column('create_date', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
