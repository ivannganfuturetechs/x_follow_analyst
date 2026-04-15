import os
import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Tweet(Base):
    __tablename__ = 'tweets'
    id = Column(String, primary_key=True)
    handle = Column(String, index=True)
    text = Column(String)
    published_at = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # One-to-many relationship with snapshots
    snapshots = relationship("EngagementSnapshot", back_populates="tweet")

class EngagementSnapshot(Base):
    __tablename__ = 'engagement_snapshots'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(String, ForeignKey('tweets.id'))
    
    views = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    
    snapshot_time = Column(DateTime, default=datetime.datetime.utcnow)
    
    tweet = relationship("Tweet", back_populates="snapshots")

def get_session():
    """Initializes the SQLite database and returns an ORM session."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(base_dir, 'data')
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = os.path.join(db_dir, 'engagement_baseline.db')
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()
