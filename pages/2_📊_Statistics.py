import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.crud import get_activities, get_time_entries_df, get_main_activity
from components.charts import (
    create_daily_hours_chart,
    create_activity_breakdown_chart,
    create_weekly_hours_chart,
    create_calendar_heatmap,
    create_progress_over_time_chart,
    create_hourly_distribution_chart,
    create_activity_comparison_chart,
    create_milestone_progress_chart,
    create_streak_chart
)
from utils.time_helpers import (
    get_time_period_bounds,
    format_duration,
    get_best_day_stats,
    get_consistency_score,
    calculate_velocity
)

st.set_page_config(
    page_title="Statistics - 10,000 Hour Tracker",
    page_icon="📊",
    layout="wide"
)

try:
    with open('assets/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass

st.title("📊 Statistics")
st.markdown("Analyze your progress and identify patterns in your learning journey")

activities = get_activities()
main_activity = get_main_activity()

if not activities:
    st.warning("⚠️ No activities found. Please add an activity from the main page first.")
    if st.button("🏠 Go to Main Page"):
        st.switch_page("app.py")
    st.stop()

st.markdown("---")
st.subheader("📅 Filter Data")

col1, col2, col3 = st.columns(3)

with col1:
    time_periods = [
        "last_7_days", "last_30_days", "last_90_days", 
        "this_week", "this_month", "this_year", "all_time"
    ]
    
    period_labels = {
        "last_7_days": "Last 7 Days",
        "last_30_days": "Last 30 Days", 
        "last_90_days": "Last 90 Days",
        "this_week": "This Week",
        "this_month": "This Month",
        "this_year": "This Year",
        "all_time": "All Time"
    }
    
    selected_period = st.selectbox(
        "Time Period",
        time_periods,
        index=1,
        format_func=lambda x: period_labels[x]
    )

with col2:
    use_custom_range = st.checkbox("Use Custom Range")
    
    if use_custom_range:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    else:
        start_date = None

with col3:
    if use_custom_range:
        end_date = st.date_input("End Date", datetime.now())
    else:
        end_date = None

if use_custom_range and start_date and end_date:
    df = get_time_entries_df(start_date, end_date)
elif selected_period == "all_time":
    df = get_time_entries_df()
else:
    period_start, period_end = get_time_period_bounds(selected_period)
    df = get_time_entries_df(period_start, period_end)

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])

st.markdown("---")
st.subheader("📈 Overview")

if not df.empty:
    total_hours = df['hours'].sum()
    total_sessions = len(df)
    active_days = df['date'].nunique()
    daily_average = total_hours / active_days if active_days > 0 else 0
    
    best_day_stats = get_best_day_stats(df)
    consistency = get_consistency_score(df)
    velocity = calculate_velocity(df)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Hours",
            value=f"{total_hours:.1f}h",
            delta=f"{total_hours:.1f}h"
        )
    
    with col2:
        st.metric(
            label="Total Sessions",
            value=f"{total_sessions:,}",
            delta=f"{total_sessions:,}"
        )
    
    with col3:
        st.metric(
            label="Active Days",
            value=f"{active_days:,}",
            delta=f"{active_days:,}"
        )
    
    with col4:
        st.metric(
            label="Daily Average",
            value=f"{daily_average:.1f}h",
            delta=f"{daily_average:.1f}h"
        )
    
    with col5:
        st.metric(
            label="Consistency",
            value=f"{consistency:.0f}%",
            delta=f"{consistency:.0f}%"
        )
    
    if best_day_stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Best Day",
                value=f"{best_day_stats['hours']:.1f}h",
                delta=best_day_stats['formatted_date']
            )
        
        with col2:
            st.metric(
                label="Weekly Velocity",
                value=f"{velocity:.1f}h/day",
                delta=f"{velocity * 7:.1f}h/week"
            )
        
        with col3:
            if main_activity:
                progress = (main_activity['total_hours'] / 10000) * 100
                st.metric(
                    label="Main Activity Progress",
                    value=f"{progress:.1f}%",
                    delta=f"{main_activity['total_hours']:.1f}h / 10,000h"
                )

else:
    st.info("📊 No data available for the selected time period.")

if not df.empty:
    st.markdown("---")
    st.subheader("📊 Charts & Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🥧 Breakdown", "📅 Calendar", "🎯 Progress"])
    
    with tab1:
        st.markdown("#### Daily Hours Over Time")
        daily_chart = create_daily_hours_chart(df)
        st.plotly_chart(daily_chart, use_container_width=True, key="daily_hours_chart")
        
        st.markdown("#### Weekly Hours")
        weekly_chart = create_weekly_hours_chart(df)
        st.plotly_chart(weekly_chart, use_container_width=True, key="weekly_hours_chart")
        
        st.markdown("#### Cumulative Progress")
        progress_chart = create_progress_over_time_chart(df)
        st.plotly_chart(progress_chart, use_container_width=True, key="progress_over_time_chart")
    
    with tab2:
        st.markdown("#### Activity Breakdown")
        breakdown_chart = create_activity_breakdown_chart(df)
        st.plotly_chart(breakdown_chart, use_container_width=True, key="activity_breakdown_chart")
        
        st.markdown("#### Activity Comparison")
        comparison_chart = create_activity_comparison_chart(activities)
        st.plotly_chart(comparison_chart, use_container_width=True, key="activity_comparison_chart_stats")
        
        st.markdown("#### Hourly Distribution")
        hourly_chart = create_hourly_distribution_chart(df)
        st.plotly_chart(hourly_chart, use_container_width=True, key="hourly_distribution_chart")
    
    with tab3:
        st.markdown("#### Activity Heatmap")
        heatmap_chart = create_calendar_heatmap(df)
        st.plotly_chart(heatmap_chart, use_container_width=True, key="calendar_heatmap_chart")
        
        st.markdown("#### Streak Analysis")
        streak_chart = create_streak_chart(df)
        st.plotly_chart(streak_chart, use_container_width=True, key="streak_analysis_chart")
    
    with tab4:
        if main_activity:
            st.markdown("#### Milestone Progress")
            milestone_chart = create_milestone_progress_chart(main_activity)
            st.plotly_chart(milestone_chart, use_container_width=True, key="milestone_progress_chart")
        
        st.markdown("#### Goal Progress by Activity")
        progress_data = []
        for activity in activities:
            progress_data.append({
                'Activity': activity['name'],
                'Hours': activity['total_hours'],
                'Progress': min(activity['total_hours'] / 10000 * 100, 100)
            })
        
        if progress_data:
            progress_df = pd.DataFrame(progress_data)
            
            fig = px.bar(
                progress_df,
                x='Activity',
                y='Progress',
                title='Progress Towards 10,000 Hours',
                labels={'Progress': 'Progress (%)', 'Activity': 'Activity'},
                color='Progress',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True, key="goal_progress_chart")

st.markdown("---")
st.subheader("🎯 Activity Details")

if activities:
    activity_names = [activity['name'] for activity in activities]
    selected_activity = st.selectbox("Select Activity for Details", activity_names)
    
    selected_activity_data = None
    for activity in activities:
        if activity['name'] == selected_activity:
            selected_activity_data = activity
            break
    
    if selected_activity_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Hours", f"{selected_activity_data['total_hours']:.1f}h")
        
        with col2:
            st.metric("Sessions", f"{selected_activity_data['session_count']:,}")
        
        with col3:
            st.metric("Daily Average", f"{selected_activity_data['daily_avg']:.1f}h")
        
        with col4:
            st.metric("Streak", f"{selected_activity_data['streak']} days")
        
        activity_df = df[df['activity_name'] == selected_activity]
        
        if not activity_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Daily Hours")
                daily_hours = activity_df.groupby('date')['hours'].sum().reset_index()
                
                fig = px.line(
                    daily_hours,
                    x='date',
                    y='hours',
                    title=f'{selected_activity} - Daily Hours',
                    markers=True
                )
                
                fig.update_traces(line_color='#3B82F6')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True, key=f"daily_hours_activity_{selected_activity}")
            
            with col2:
                st.markdown("##### Progress Ring")
                from components.progress_ring import create_mini_progress_ring
                
                progress_ring = create_mini_progress_ring(
                    selected_activity_data['total_hours'],
                    selected_activity
                )
                st.plotly_chart(progress_ring, use_container_width=True, key=f"progress_ring_stats_{selected_activity}")
        
        if not activity_df.empty:
            st.markdown("##### Recent Sessions")
            recent_sessions = activity_df.tail(10).sort_values('date', ascending=False)
            
            display_sessions = recent_sessions[['date', 'hours', 'notes']].copy()
            display_sessions['date'] = display_sessions['date'].dt.strftime('%Y-%m-%d')
            display_sessions['hours'] = display_sessions['hours'].apply(lambda x: f"{x:.2f}h")
            display_sessions.columns = ['Date', 'Hours', 'Notes']
            
            st.dataframe(display_sessions, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("💾 Export Data")

col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Download CSV", use_container_width=True):
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Time Entries",
                data=csv,
                file_name=f"time_entries_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.error("No data to export")

with col2:
    if st.button("📊 Generate Report", use_container_width=True):
        if not df.empty:
            report_text = f"""
10,000 Hour Tracker Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW
========
Total Hours: {df['hours'].sum():.1f}h
Total Sessions: {len(df):,}
Active Days: {df['date'].nunique():,}
Daily Average: {df['hours'].sum() / df['date'].nunique():.1f}h

ACTIVITY BREAKDOWN
==================
"""
            
            activity_summary = df.groupby('activity_name')['hours'].sum().sort_values(ascending=False)
            for activity, hours in activity_summary.items():
                report_text += f"{activity}: {hours:.1f}h\n"
            
            st.download_button(
                label="Download Report",
                data=report_text,
                file_name=f"progress_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        else:
            st.error("No data to generate report")

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("⏱️ Timer", use_container_width=True):
        st.switch_page("pages/1_⏱️_Timer.py")

with col3:
    if st.button("🎯 Activities", use_container_width=True):
        st.switch_page("pages/3_🎯_Activities.py") 