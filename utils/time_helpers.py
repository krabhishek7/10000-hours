from datetime import datetime, timedelta
import pandas as pd

def format_duration(hours):
    """Format hours as human-readable duration."""
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes} min"
    elif hours < 24:
        return f"{hours:.1f} hours"
    else:
        days = int(hours // 24)
        remaining_hours = hours % 24
        if remaining_hours < 1:
            return f"{days} day{'s' if days != 1 else ''}"
        else:
            return f"{days} day{'s' if days != 1 else ''} {remaining_hours:.1f} hours"

def calculate_daily_average(total_hours, start_date):
    """Calculate daily average hours since start date."""
    if not start_date:
        return 0
    
    days_since_start = (datetime.now() - start_date).days + 1
    return total_hours / days_since_start if days_since_start > 0 else 0

def estimate_completion_date(current_hours, target_hours=10000, daily_average=None):
    """Estimate completion date based on current progress and daily average."""
    if not daily_average or daily_average <= 0:
        return None
    
    remaining_hours = target_hours - current_hours
    days_needed = remaining_hours / daily_average
    completion_date = datetime.now() + timedelta(days=days_needed)
    
    return completion_date

def get_time_period_bounds(period):
    """Get start and end dates for different time periods."""
    now = datetime.now()
    today = now.date()
    
    if period == "today":
        start_date = today
        end_date = today
    elif period == "yesterday":
        yesterday = today - timedelta(days=1)
        start_date = yesterday
        end_date = yesterday
    elif period == "this_week":
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif period == "last_week":
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = today - timedelta(days=today.weekday() + 1)
    elif period == "this_month":
        start_date = today.replace(day=1)
        end_date = today
    elif period == "last_month":
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        start_date = last_day_last_month.replace(day=1)
        end_date = last_day_last_month
    elif period == "this_year":
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif period == "last_7_days":
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == "last_30_days":
        start_date = today - timedelta(days=30)
        end_date = today
    elif period == "last_90_days":
        start_date = today - timedelta(days=90)
        end_date = today
    else:
        # Default to last 30 days
        start_date = today - timedelta(days=30)
        end_date = today
    
    return start_date, end_date

def calculate_streak(df):
    """Calculate current streak of consecutive days with activity."""
    if df.empty:
        return 0
    
    # Group by date and sum hours
    daily_hours = df.groupby('date')['hours'].sum().reset_index()
    daily_hours = daily_hours.sort_values('date', ascending=False)
    
    streak = 0
    current_date = datetime.now().date()
    
    for _, row in daily_hours.iterrows():
        # Convert pandas datetime to date for comparison
        row_date = pd.to_datetime(row['date']).date()
        
        if row_date == current_date and row['hours'] > 0:
            streak += 1
            current_date -= timedelta(days=1)
        elif row_date == current_date and row['hours'] == 0:
            break
        elif row_date < current_date:
            # Check if there are any missing days
            days_gap = (current_date - row_date).days
            if days_gap > 1:
                break
            elif row['hours'] > 0:
                streak += 1
                current_date = row_date - timedelta(days=1)
            else:
                break
    
    return streak

def get_week_dates(date):
    """Get start and end dates of the week containing the given date."""
    start_of_week = date - timedelta(days=date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def get_month_dates(date):
    """Get start and end dates of the month containing the given date."""
    start_of_month = date.replace(day=1)
    if date.month == 12:
        end_of_month = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
    return start_of_month, end_of_month

def parse_time_input(time_str):
    """Parse time input in various formats (e.g., '2h 30m', '2.5h', '150m')."""
    if not time_str:
        return 0
    
    time_str = time_str.lower().strip()
    
    # Remove spaces
    time_str = time_str.replace(' ', '')
    
    total_hours = 0
    
    # Handle formats like "2h30m" or "2h"
    if 'h' in time_str:
        parts = time_str.split('h')
        if parts[0]:
            total_hours += float(parts[0])
        if len(parts) > 1 and parts[1]:
            minutes_part = parts[1].replace('m', '')
            if minutes_part:
                total_hours += float(minutes_part) / 60
    
    # Handle formats like "150m"
    elif 'm' in time_str:
        minutes = float(time_str.replace('m', ''))
        total_hours = minutes / 60
    
    # Handle decimal hours like "2.5"
    else:
        try:
            total_hours = float(time_str)
        except ValueError:
            return 0
    
    return total_hours

def format_time_remaining(hours_remaining, daily_average):
    """Format time remaining to reach goal."""
    if daily_average <= 0:
        return "Unable to calculate"
    
    days_remaining = hours_remaining / daily_average
    
    if days_remaining < 1:
        return "Less than 1 day"
    elif days_remaining < 7:
        return f"{days_remaining:.1f} days"
    elif days_remaining < 30:
        weeks = days_remaining / 7
        return f"{weeks:.1f} weeks"
    elif days_remaining < 365:
        months = days_remaining / 30
        return f"{months:.1f} months"
    else:
        years = days_remaining / 365
        return f"{years:.1f} years"

def get_productivity_score(total_hours, target_hours=10000):
    """Calculate a productivity score based on progress."""
    if target_hours == 0:
        return 0
    
    progress = (total_hours / target_hours) * 100
    
    if progress >= 100:
        return 100
    elif progress >= 75:
        return 90 + (progress - 75) / 25 * 10
    elif progress >= 50:
        return 70 + (progress - 50) / 25 * 20
    elif progress >= 25:
        return 40 + (progress - 25) / 25 * 30
    else:
        return progress / 25 * 40

def calculate_velocity(df, days=7):
    """Calculate velocity (hours per day) over the last N days."""
    if df.empty:
        return 0
    
    cutoff_date = datetime.now().date() - timedelta(days=days)
    # Convert cutoff_date to pandas datetime for comparison
    cutoff_datetime = pd.Timestamp(cutoff_date)
    recent_data = df[df['date'] >= cutoff_datetime]
    
    if recent_data.empty:
        return 0
    
    total_hours = recent_data['hours'].sum()
    return total_hours / days

def get_best_day_stats(df):
    """Get statistics for the best day."""
    if df.empty:
        return None
    
    daily_hours = df.groupby('date')['hours'].sum().reset_index()
    best_day = daily_hours.loc[daily_hours['hours'].idxmax()]
    
    # Convert pandas datetime to datetime for formatting
    best_date = pd.to_datetime(best_day['date'])
    
    return {
        'date': best_day['date'],
        'hours': best_day['hours'],
        'formatted_date': best_date.strftime('%B %d, %Y')
    }

def get_consistency_score(df, days=30):
    """Calculate consistency score based on regular activity."""
    if df.empty:
        return 0
    
    cutoff_date = datetime.now().date() - timedelta(days=days)
    # Convert cutoff_date to pandas datetime for comparison
    cutoff_datetime = pd.Timestamp(cutoff_date)
    recent_data = df[df['date'] >= cutoff_datetime]
    
    if recent_data.empty:
        return 0
    
    daily_hours = recent_data.groupby('date')['hours'].sum().reset_index()
    active_days = len(daily_hours[daily_hours['hours'] > 0])
    
    consistency = (active_days / days) * 100
    return min(consistency, 100)  # Cap at 100% 