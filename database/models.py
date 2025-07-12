from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Activity(Base):
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    category = Column(String(50))
    is_main = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    color = Column(String(7), default='#3B82F6')

class TimeEntry(Base):
    __tablename__ = 'time_entries'
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, nullable=False)
    hours = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.now)
    notes = Column(String(500))

class Milestone(Base):
    __tablename__ = 'milestones'
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, nullable=False)
    hours_reached = Column(Integer, nullable=False)
    reached_at = Column(DateTime, default=datetime.now) 