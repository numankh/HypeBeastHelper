"""empty message

Revision ID: 550773a94207
Revises: 2326c222c87b
Create Date: 2021-11-14 08:39:58.017925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '550773a94207'
down_revision = '2326c222c87b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shoes', sa.Column('desc_fre_score', sa.Integer(), nullable=True))
    op.add_column('shoes', sa.Column('desc_avg_grade_score', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shoes', 'desc_avg_grade_score')
    op.drop_column('shoes', 'desc_fre_score')
    # ### end Alembic commands ###