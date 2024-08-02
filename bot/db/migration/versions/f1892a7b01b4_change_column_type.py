"""change column type

Revision ID: f1892a7b01b4
Revises: 0f9462045173
Create Date: 2024-08-02 12:43:40.931606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1892a7b01b4'
down_revision: Union[str, None] = '0f9462045173'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('notifications', 'notification_id',
               existing_type=sa.UUID(),
               type_=sa.BIGINT(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text('gen_random_uuid()'))
    op.alter_column('user_notifications', 'notification_id',
               existing_type=sa.UUID(),
               type_=sa.BIGINT(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_notifications', 'notification_id',
               existing_type=sa.BIGINT(),
               type_=sa.UUID(),
               existing_nullable=False)
    op.alter_column('notifications', 'notification_id',
               existing_type=sa.BIGINT(),
               type_=sa.UUID(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text('gen_random_uuid()'))
    # ### end Alembic commands ###