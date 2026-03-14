from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

os.makedirs('data', exist_ok=True)

engine = create_engine('sqlite:///data/bot.db?check_same_thread=False')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Dream(Base):
    __tablename__ = 'dreams'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    dream_text = Column(Text, nullable=False)
    interpretation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    mood = Column(String, nullable=True)

class MoodEntry(Base):
    __tablename__ = 'moods'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    mood = Column(String)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)

def get_user(session, user_id, first_name=None, username=None):
    user = session.query(User).filter_by(user_id=user_id).first()
    if not user and first_name:
        user = User(user_id=user_id, first_name=first_name, username=username)
        session.add(user)
        session.commit()
    return user

def save_dream(session, user_id, dream_text, interpretation=None, mood=None):
    dream = Dream(user_id=user_id, dream_text=dream_text, interpretation=interpretation, mood=mood)
    session.add(dream)
    session.commit()
    return dream

def get_last_dreams(session, user_id, limit=5):
    return session.query(Dream).filter_by(user_id=user_id).order_by(Dream.created_at.desc()).limit(limit).all()

def save_mood(session, user_id, mood, note=None):
    entry = MoodEntry(user_id=user_id, mood=mood, note=note)
    session.add(entry)
    session.commit()
