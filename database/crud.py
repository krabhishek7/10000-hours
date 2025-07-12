from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Activity, TimeEntry, Milestone
from .database import SessionLocal
from datetime import datetime, timedelta
import pandas as pd

def get_db_session():
    """Get a database session."""
    return SessionLocal()

def get_activities():
    """Get all activities with their statistics."""
    db = get_db_session()
    try:
        activities = db.query(Activity).all()
        activity_stats = []
        
        for activity in activities:
            # Calculate total hours
            total_hours = db.query(func.sum(TimeEntry.hours)).filter(
                TimeEntry.activity_id == activity.id
            ).scalar() or 0
            
            # Calculate today's hours
            today = datetime.now().date()
            today_hours = db.query(func.sum(TimeEntry.hours)).filter(
                TimeEntry.activity_id == activity.id,
                func.date(TimeEntry.date) == today
            ).scalar() or 0
            
            # Calculate week's hours
            week_start = today - timedelta(days=today.weekday())
            week_hours = db.query(func.sum(TimeEntry.hours)).filter(
                TimeEntry.activity_id == activity.id,
                func.date(TimeEntry.date) >= week_start
            ).scalar() or 0
            
            # Calculate daily average
            first_entry = db.query(func.min(TimeEntry.date)).filter(
                TimeEntry.activity_id == activity.id
            ).scalar()
            
            if first_entry:
                days_active = (datetime.now() - first_entry).days + 1
                daily_avg = total_hours / days_active if days_active > 0 else 0
            else:
                daily_avg = 0
            
            # Calculate session count
            session_count = db.query(TimeEntry).filter(
                TimeEntry.activity_id == activity.id
            ).count()
            
            # Calculate streak (simplified)
            streak = 0
            current_date = datetime.now().date()
            while True:
                has_entry = db.query(TimeEntry).filter(
                    TimeEntry.activity_id == activity.id,
                    func.date(TimeEntry.date) == current_date
                ).first()
                if has_entry:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            activity_stats.append({
                'id': activity.id,
                'name': activity.name,
                'description': activity.description,
                'category': activity.category,
                'is_main': activity.is_main,
                'color': activity.color,
                'total_hours': total_hours,
                'today_hours': today_hours,
                'week_hours': week_hours,
                'daily_avg': daily_avg,
                'session_count': session_count,
                'streak': streak
            })
        
        return activity_stats
    finally:
        db.close()

def get_main_activity():
    """Get the main activity with its statistics."""
    db = get_db_session()
    try:
        main_activity = db.query(Activity).filter(Activity.is_main == True).first()
        if not main_activity:
            return None
        
        # Calculate statistics
        total_hours = db.query(func.sum(TimeEntry.hours)).filter(
            TimeEntry.activity_id == main_activity.id
        ).scalar() or 0
        
        today = datetime.now().date()
        today_hours = db.query(func.sum(TimeEntry.hours)).filter(
            TimeEntry.activity_id == main_activity.id,
            func.date(TimeEntry.date) == today
        ).scalar() or 0
        
        week_start = today - timedelta(days=today.weekday())
        week_hours = db.query(func.sum(TimeEntry.hours)).filter(
            TimeEntry.activity_id == main_activity.id,
            func.date(TimeEntry.date) >= week_start
        ).scalar() or 0
        
        # Calculate daily average
        first_entry = db.query(func.min(TimeEntry.date)).filter(
            TimeEntry.activity_id == main_activity.id
        ).scalar()
        
        if first_entry:
            days_active = (datetime.now() - first_entry).days + 1
            daily_avg = total_hours / days_active if days_active > 0 else 0
        else:
            daily_avg = 0
        
        return {
            'id': main_activity.id,
            'name': main_activity.name,
            'description': main_activity.description,
            'total_hours': total_hours,
            'today_hours': today_hours,
            'week_hours': week_hours,
            'daily_avg': daily_avg
        }
    finally:
        db.close()

def add_activity(name, description="", category="", is_main=False, color="#3B82F6"):
    """Add a new activity."""
    db = get_db_session()
    try:
        # If setting as main, unset other main activities
        if is_main:
            db.query(Activity).filter(Activity.is_main == True).update({Activity.is_main: False})
        
        activity = Activity(
            name=name,
            description=description,
            category=category,
            is_main=is_main,
            color=color
        )
        db.add(activity)
        db.commit()
        return activity.id
    finally:
        db.close()

def update_activity(activity_id, name=None, description=None, category=None, is_main=None, color=None):
    """Update an existing activity."""
    db = get_db_session()
    try:
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            return False
        
        if name is not None:
            activity.name = name
        if description is not None:
            activity.description = description
        if category is not None:
            activity.category = category
        if color is not None:
            activity.color = color
        if is_main is not None:
            if is_main:
                # Unset other main activities
                db.query(Activity).filter(Activity.is_main == True).update({Activity.is_main: False})
            activity.is_main = is_main
        
        db.commit()
        return True
    finally:
        db.close()

def delete_activity(activity_id):
    """Delete an activity and all its time entries."""
    db = get_db_session()
    try:
        # Delete time entries first
        db.query(TimeEntry).filter(TimeEntry.activity_id == activity_id).delete()
        # Delete milestones
        db.query(Milestone).filter(Milestone.activity_id == activity_id).delete()
        # Delete activity
        db.query(Activity).filter(Activity.id == activity_id).delete()
        db.commit()
        return True
    finally:
        db.close()

def add_time_entry(activity_id, hours, date=None, notes=""):
    """Add a time entry for an activity."""
    db = get_db_session()
    try:
        if date is None:
            date = datetime.now()
        
        entry = TimeEntry(
            activity_id=activity_id,
            hours=hours,
            date=date,
            notes=notes
        )
        db.add(entry)
        db.commit()
        
        # Check for milestones
        total_hours = db.query(func.sum(TimeEntry.hours)).filter(
            TimeEntry.activity_id == activity_id
        ).scalar() or 0
        
        milestones = [100, 500, 1000, 2500, 5000, 7500, 10000]
        for milestone in milestones:
            if total_hours >= milestone:
                # Check if milestone already exists
                existing = db.query(Milestone).filter(
                    Milestone.activity_id == activity_id,
                    Milestone.hours_reached == milestone
                ).first()
                if not existing:
                    milestone_entry = Milestone(
                        activity_id=activity_id,
                        hours_reached=milestone
                    )
                    db.add(milestone_entry)
        
        db.commit()
        return True
    finally:
        db.close()

def get_time_entries_df(start_date=None, end_date=None):
    """Get time entries as a pandas DataFrame."""
    db = get_db_session()
    try:
        query = db.query(TimeEntry, Activity.name.label('activity_name')).join(
            Activity, TimeEntry.activity_id == Activity.id
        )
        
        if start_date:
            query = query.filter(func.date(TimeEntry.date) >= start_date)
        if end_date:
            query = query.filter(func.date(TimeEntry.date) <= end_date)
        
        results = query.all()
        
        data = []
        for entry, activity_name in results:
            data.append({
                'id': entry.id,
                'activity_id': entry.activity_id,
                'activity_name': activity_name,
                'hours': entry.hours,
                'date': entry.date.date(),
                'notes': entry.notes
            })
        
        return pd.DataFrame(data)
    finally:
        db.close()

def get_activity_names():
    """Get all activity names."""
    db = get_db_session()
    try:
        activities = db.query(Activity.name).all()
        return [activity.name for activity in activities]
    finally:
        db.close()

def get_milestones(activity_id):
    """Get milestones for an activity."""
    db = get_db_session()
    try:
        milestones = db.query(Milestone).filter(
            Milestone.activity_id == activity_id
        ).order_by(Milestone.hours_reached).all()
        return milestones
    finally:
        db.close() 