"""create news and news_topics tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # news table
    op.create_table('news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.SmallInteger(), nullable=False, server_default='1'),
        sa.Column('published_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
    )
    op.create_index(op.f('ix_news_id'), 'news', ['id'], unique=False)
    op.create_index(op.f('ix_news_slug'), 'news', ['slug'], unique=True)
    op.create_index('idx_news_status_published', 'news', ['status', sa.text('published_at DESC')])
    op.create_index(op.f('ix_news_author_id'), 'news', ['author_id'], unique=False)

    # news_topics junction table
    op.create_table('news_topics',
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('news_id', 'topic_id'),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_news_topics_news_id'), 'news_topics', ['news_id'], unique=False)
    op.create_index(op.f('ix_news_topics_topic_id'), 'news_topics', ['topic_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_news_topics_topic_id'), table_name='news_topics')
    op.drop_index(op.f('ix_news_topics_news_id'), table_name='news_topics')
    op.drop_table('news_topics')
    op.drop_index(op.f('ix_news_author_id'), table_name='news')
    op.drop_index('idx_news_status_published', table_name='news')
    op.drop_index(op.f('ix_news_slug'), table_name='news')
    op.drop_index(op.f('ix_news_id'), table_name='news')
    op.drop_table('news')
