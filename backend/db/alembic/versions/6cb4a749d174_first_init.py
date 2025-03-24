"""first init

Revision ID: 6cb4a749d174
Revises:
Create Date: 2025-02-19 12:12:20.439816

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cb4a749d174'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'Group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(length=300), nullable=False),
        sa.Column('is_personal_group', sa.BOOLEAN(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title'),
    )
    op.create_table(
        'Permission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=24), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title'),
    )
    op.create_table(
        'Usr',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=16), nullable=False),
        sa.Column('name_account', sa.String(length=24), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('is_bot', sa.Boolean(), nullable=False),
        sa.Column('avatar', sa.String(), nullable=True),
        sa.Column('panorama', sa.String(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('name_account'),
    )
    op.create_table(
        'Chat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['Group.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title'),
    )
    op.create_table(
        'Role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=24), nullable=False),
        sa.Column('priority', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['Group.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'Token',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['Usr.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_table(
        'UsrGroup',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['Group.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['Usr.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'Message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('local_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['chat_id'],
            ['Chat.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['Usr.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chat_id', 'local_id', name='unique_chat_local_id'),
    )
    op.create_table(
        'RolePermission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['permission_id'],
            ['Permission.id'],
        ),
        sa.ForeignKeyConstraint(
            ['role_id'],
            ['Role.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'RoleUsrGroup',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('usergroup_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['role_id'],
            ['Role.id'],
        ),
        sa.ForeignKeyConstraint(
            ['usergroup_id'],
            ['UsrGroup.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'UsrReadedMessages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['message_id'],
            ['Message.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['Usr.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('UsrReadedMessages')
    op.drop_table('RoleUsrGroup')
    op.drop_table('RolePermission')
    op.drop_table('Message')
    op.drop_table('UsrGroup')
    op.drop_table('Token')
    op.drop_table('Role')
    op.drop_table('Chat')
    op.drop_table('Usr')
    op.drop_table('Permission')
    op.drop_table('Group')
    # ### end Alembic commands ###
