from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Text, TIMESTAMP, SmallInteger, Table, text
from sqlalchemy.orm import relationship

news_topics = Table(
    "news_topics",
    Base.metadata,
    Column("news_id", Integer, ForeignKey("news.id", ondelete="CASCADE"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True),
)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    status = Column(SmallInteger, nullable=False, default=1)
    published_at = Column(TIMESTAMP(timezone=True), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    topics = relationship("Topic", secondary=news_topics, lazy="selectin")
