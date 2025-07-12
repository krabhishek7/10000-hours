import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

def create_daily_hours_chart(df):
    """Create a line chart showing daily hours."""
    if df.empty:
        return create_empty_chart("No data available")
    
    daily_hours = df.groupby('date')['hours'].sum().reset_index()
    
    fig = px.line(
        daily_hours, 
        x='date', 
        y='hours',
        title='Daily Hours Tracked',
        labels={'hours': 'Hours', 'date': 'Date'},
        markers=True
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(
        line=dict(color='#22C55E', width=3),
        marker=dict(color='#22C55E', size=8)
    )
    
    return fig

def create_activity_breakdown_chart(df):
    """Create a pie chart showing activity breakdown."""
    if df.empty:
        return create_empty_chart("No data available")
    
    activity_hours = df.groupby('activity_name')['hours'].sum().reset_index()
    
    fig = px.pie(
        activity_hours,
        values='hours',
        names='activity_name',
        title='Time Distribution by Activity'
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_weekly_hours_chart(df):
    """Create a bar chart showing weekly hours."""
    if df.empty:
        return create_empty_chart("No data available")
    
    # Add week information
    df['week'] = df['date'].dt.isocalendar().week
    df['year'] = df['date'].dt.year
    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.dayofweek, unit='d')
    
    weekly_hours = df.groupby('week_start')['hours'].sum().reset_index()
    
    fig = px.bar(
        weekly_hours,
        x='week_start',
        y='hours',
        title='Weekly Hours Tracked',
        labels={'hours': 'Hours', 'week_start': 'Week Starting'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(marker_color='#22C55E')
    
    return fig

def create_calendar_heatmap(df):
    """Create a calendar heatmap showing daily activity."""
    if df.empty:
        return create_empty_chart("No data available")
    
    # Prepare data for heatmap
    daily_hours = df.groupby('date')['hours'].sum().reset_index()
    daily_hours['day_of_week'] = daily_hours['date'].dt.dayofweek
    daily_hours['week_of_year'] = daily_hours['date'].dt.isocalendar().week
    
    # Create matrix for heatmap
    max_week = daily_hours['week_of_year'].max()
    heatmap_data = np.zeros((7, max_week))
    
    for _, row in daily_hours.iterrows():
        heatmap_data[row['day_of_week'], row['week_of_year']-1] = row['hours']
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title="Hours")
    ))
    
    fig.update_layout(
        title='Activity Heatmap',
        xaxis_title='Week of Year',
        yaxis_title='Day of Week',
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        ),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_progress_over_time_chart(df):
    """Create a chart showing cumulative progress over time."""
    if df.empty:
        return create_empty_chart("No data available")
    
    # Calculate cumulative hours
    df_sorted = df.sort_values('date')
    cumulative_hours = df_sorted.groupby('date')['hours'].sum().cumsum().reset_index()
    
    fig = px.area(
        cumulative_hours,
        x='date',
        y='hours',
        title='Cumulative Hours Over Time',
        labels={'hours': 'Total Hours', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(fill='tonexty', fillcolor='rgba(59, 130, 246, 0.3)')
    
    return fig

def create_hourly_distribution_chart(df):
    """Create a chart showing hour distribution throughout the day."""
    if df.empty:
        return create_empty_chart("No data available")
    
    # Extract hour from date
    df['hour'] = df['date'].dt.hour
    hourly_dist = df.groupby('hour')['hours'].sum().reset_index()
    
    fig = px.bar(
        hourly_dist,
        x='hour',
        y='hours',
        title='Time Distribution by Hour of Day',
        labels={'hours': 'Total Hours', 'hour': 'Hour of Day'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(marker_color='#4ADE80')
    
    return fig

def create_activity_comparison_chart(activities_data):
    """Create a horizontal bar chart comparing activities."""
    if not activities_data:
        return create_empty_chart("No activities available")
    
    df = pd.DataFrame(activities_data)
    
    fig = px.bar(
        df,
        x='total_hours',
        y='name',
        orientation='h',
        title='Activity Comparison',
        labels={'total_hours': 'Total Hours', 'name': 'Activity'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(marker_color='#16A34A')
    
    return fig

def create_milestone_progress_chart(activity_data):
    """Create a chart showing milestone progress."""
    milestones = [100, 500, 1000, 2500, 5000, 7500, 10000]
    current_hours = activity_data.get('total_hours', 0)
    
    progress = []
    for milestone in milestones:
        if current_hours >= milestone:
            progress.append(100)
        else:
            progress.append(0)
    
    fig = go.Figure(data=[
        go.Bar(
            x=milestones,
            y=progress,
            marker_color=['#10B981' if p == 100 else '#E5E7EB' for p in progress]
        )
    ])
    
    fig.update_layout(
        title='Milestone Progress',
        xaxis_title='Milestone (Hours)',
        yaxis_title='Progress (%)',
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_empty_chart(message):
    """Create an empty chart with a message."""
    fig = go.Figure()
    
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text=message,
        showarrow=False,
        font=dict(size=16, color='#6B7280'),
        xref="paper",
        yref="paper"
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    
    return fig

def create_streak_chart(df):
    """Create a chart showing daily streak."""
    if df.empty:
        return create_empty_chart("No data available")
    
    # Calculate streaks
    daily_hours = df.groupby('date')['hours'].sum().reset_index()
    daily_hours['has_activity'] = daily_hours['hours'] > 0
    
    # Simple streak calculation
    streaks = []
    current_streak = 0
    
    for has_activity in daily_hours['has_activity']:
        if has_activity:
            current_streak += 1
        else:
            current_streak = 0
        streaks.append(current_streak)
    
    daily_hours['streak'] = streaks
    
    fig = px.line(
        daily_hours,
        x='date',
        y='streak',
        title='Daily Streak',
        labels={'streak': 'Streak (Days)', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(line=dict(color='#16A34A', width=3))
    
    return fig 