import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
from database.crud import get_activities, add_time_entry, get_activity_names
from components.timer import timer
from utils.time_helpers import parse_time_input, format_duration

# Page config
st.set_page_config(
    page_title="Timer - 10,000 Hour Tracker",
    page_icon="⏱️",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass

st.title("⏱️ Timer")
st.markdown("Track your time with precision and flexibility")

# Get activities
activities = get_activities()

if not activities:
    st.warning("⚠️ No activities found. Please add an activity from the main page first.")
    if st.button("🏠 Go to Main Page"):
        st.switch_page("app.py")
    st.stop()

# Timer section
st.markdown("---")
st.subheader("🎯 Active Timer")

# Current timer status
if timer.is_running():
    # Display current timer
    current_activity_id = timer.get_current_activity_id()
    current_activity = None
    for activity in activities:
        if activity['id'] == current_activity_id:
            current_activity = activity
            break
    
    if current_activity:
        st.markdown(f"**Currently tracking:** {current_activity['name']}")
        
        # Timer display
        col1, col2 = st.columns([2, 1])
        
        with col1:
            elapsed = timer.get_elapsed_time()
            time_details = timer.format_time_detailed(elapsed)
            
            status = "⏸️ PAUSED" if st.session_state.get('is_paused', False) else "⏱️ RUNNING"
            status_class = "paused" if st.session_state.get('is_paused', False) else "running"
            
            st.markdown(f"""
                <div class="timer-display {status_class}">
                    <div class="timer-status">{status}</div>
                    <div style="display: flex; justify-content: center; align-items: baseline; gap: 1rem; margin: 1rem 0;">
                        <div style="text-align: center;">
                            <div style="font-size: 3rem; font-weight: 700; color: var(--primary-color); font-family: 'Monaco', monospace;">{time_details['hours']:02d}</div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px;">Hours</div>
                        </div>
                        <div style="font-size: 2rem; color: var(--text-secondary); margin: 0 0.5rem;">:</div>
                        <div style="text-align: center;">
                            <div style="font-size: 3rem; font-weight: 700; color: var(--primary-color); font-family: 'Monaco', monospace;">{time_details['minutes']:02d}</div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px;">Minutes</div>
                        </div>
                        <div style="font-size: 2rem; color: var(--text-secondary); margin: 0 0.5rem;">:</div>
                        <div style="text-align: center;">
                            <div style="font-size: 3rem; font-weight: 700; color: var(--primary-color); font-family: 'Monaco', monospace;">{time_details['seconds']:02d}</div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px;">Seconds</div>
                        </div>
                    </div>
                    <div style="margin-top: 1rem;">
                        <div style="font-size: 1.25rem; color: var(--text-secondary);">Total: {time_details['formatted']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Timer controls
            if st.session_state.get('is_paused', False):
                if st.button("▶️ Resume", use_container_width=True, type="primary"):
                    timer.resume_timer()
                    st.session_state.is_paused = False
                    st.rerun()
            else:
                if st.button("⏸️ Pause", use_container_width=True):
                    timer.pause_timer()
                    st.session_state.is_paused = True
                    st.rerun()
            
            if st.button("⏹️ Stop Timer", use_container_width=True, type="secondary"):
                hours_added = timer.stop_timer()
                if hours_added > 0:
                    st.success(f"✅ Added {hours_added:.2f} hours to {current_activity['name']}")
                    st.session_state.is_paused = False
                    st.rerun()
                else:
                    st.error("❌ Failed to stop timer")
        
        # Auto-refresh for running timer
        if not st.session_state.get('is_paused', False):
            time.sleep(1)
            st.rerun()
    
else:
    # Start new timer
    st.markdown("**No active timer**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Activity selection
        activity_names = [activity['name'] for activity in activities]
        selected_activity_name = st.selectbox("Select Activity", activity_names)
        
        # Find activity ID
        selected_activity_id = None
        for activity in activities:
            if activity['name'] == selected_activity_name:
                selected_activity_id = activity['id']
                break
    
    with col2:
        if st.button("▶️ Start Timer", use_container_width=True, type="primary"):
            if timer.start_timer(selected_activity_id):
                st.success("✅ Timer started!")
                st.rerun()
            else:
                st.error("❌ Failed to start timer")

# Manual time entry
st.markdown("---")
st.subheader("📝 Manual Time Entry")

with st.form("manual_entry"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Activity selection
        activity_names = [activity['name'] for activity in activities]
        selected_activity = st.selectbox("Activity", activity_names, key="manual_activity")
    
    with col2:
        # Time input with flexible parsing
        time_input = st.text_input("Time", placeholder="2h 30m, 2.5h, or 150m", help="Enter time in various formats")
        
        # Also provide number input as backup
        hours_input = st.number_input("Or Hours", min_value=0.0, max_value=24.0, step=0.25, value=0.0)
    
    with col3:
        # Date input
        date = st.date_input("Date", datetime.now())
    
    # Notes
    notes = st.text_area("Notes (optional)", placeholder="What did you work on?")
    
    submitted = st.form_submit_button("Add Entry", use_container_width=True)
    
    if submitted:
        # Parse time input
        if time_input:
            hours = parse_time_input(time_input)
        else:
            hours = hours_input
        
        if hours > 0:
            # Find activity ID
            activity_id = None
            for activity in activities:
                if activity['name'] == selected_activity:
                    activity_id = activity['id']
                    break
            
            if activity_id:
                success = add_time_entry(
                    activity_id=activity_id,
                    hours=hours,
                    date=datetime.combine(date, datetime.min.time()),
                    notes=notes
                )
                
                if success:
                    st.success(f"✅ Added {hours:.2f} hours to {selected_activity}")
                    st.rerun()
                else:
                    st.error("❌ Failed to add time entry")
        else:
            st.error("❌ Please enter a valid time amount")

# Pomodoro Timer
st.markdown("---")
st.subheader("🍅 Pomodoro Timer")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("**Focus sessions with built-in breaks**")
    
    # Pomodoro settings
    pomodoro_col1, pomodoro_col2, pomodoro_col3 = st.columns(3)
    
    with pomodoro_col1:
        work_minutes = st.number_input("Work Minutes", min_value=15, max_value=60, value=25, step=5)
    
    with pomodoro_col2:
        break_minutes = st.number_input("Break Minutes", min_value=5, max_value=15, value=5, step=1)
    
    with pomodoro_col3:
        sessions = st.number_input("Sessions", min_value=1, max_value=10, value=4, step=1)
    
    # Activity for Pomodoro
    activity_names = [activity['name'] for activity in activities]
    pomodoro_activity = st.selectbox("Activity for Pomodoro", activity_names, key="pomodoro_activity")

with col2:
    if st.button("🍅 Start Pomodoro", use_container_width=True, type="primary"):
        st.session_state.pomodoro_running = True
        st.session_state.pomodoro_session = 1
        st.session_state.pomodoro_work_time = work_minutes
        st.session_state.pomodoro_break_time = break_minutes
        st.session_state.pomodoro_total_sessions = sessions
        st.session_state.pomodoro_activity = pomodoro_activity
        st.session_state.pomodoro_start_time = datetime.now()
        st.session_state.pomodoro_is_break = False
        st.rerun()

# Pomodoro timer display
if st.session_state.get('pomodoro_running', False):
    st.markdown("---")
    st.markdown("### 🍅 Pomodoro Session in Progress")
    
    current_session = st.session_state.pomodoro_session
    total_sessions = st.session_state.pomodoro_total_sessions
    is_break = st.session_state.get('pomodoro_is_break', False)
    
    # Calculate elapsed time
    elapsed_time = datetime.now() - st.session_state.pomodoro_start_time
    
    if is_break:
        total_time = st.session_state.pomodoro_break_time * 60
        session_type = "Break"
    else:
        total_time = st.session_state.pomodoro_work_time * 60
        session_type = "Work"
    
    remaining_seconds = total_time - elapsed_time.total_seconds()
    
    if remaining_seconds <= 0:
        # Session completed
        if is_break:
            # Break finished, start next work session
            st.session_state.pomodoro_session += 1
            st.session_state.pomodoro_is_break = False
            st.session_state.pomodoro_start_time = datetime.now()
            
            if st.session_state.pomodoro_session > total_sessions:
                # All sessions completed
                st.success("🎉 Pomodoro sequence completed!")
                st.balloons()
                
                # Add time entry for all work sessions
                total_work_hours = (st.session_state.pomodoro_work_time * total_sessions) / 60
                
                # Find activity ID
                activity_id = None
                for activity in activities:
                    if activity['name'] == st.session_state.pomodoro_activity:
                        activity_id = activity['id']
                        break
                
                if activity_id:
                    add_time_entry(
                        activity_id=activity_id,
                        hours=total_work_hours,
                        date=datetime.now(),
                        notes=f"Pomodoro session: {total_sessions} sessions x {st.session_state.pomodoro_work_time} minutes"
                    )
                
                # Reset pomodoro state
                st.session_state.pomodoro_running = False
                st.rerun()
            else:
                st.info(f"Starting session {st.session_state.pomodoro_session} of {total_sessions}")
                st.rerun()
        else:
            # Work session finished, start break
            st.session_state.pomodoro_is_break = True
            st.session_state.pomodoro_start_time = datetime.now()
            st.info("Work session complete! Starting break...")
            st.rerun()
    else:
        # Display timer
        minutes_remaining = int(remaining_seconds // 60)
        seconds_remaining = int(remaining_seconds % 60)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Progress bar
            progress = (total_time - remaining_seconds) / total_time
            st.progress(progress)
            
            # Time display
            if is_break:
                st.markdown(f"### 🛌 Break Time: {minutes_remaining:02d}:{seconds_remaining:02d}")
            else:
                st.markdown(f"### 💪 Work Time: {minutes_remaining:02d}:{seconds_remaining:02d}")
            
            st.markdown(f"**Session {current_session} of {total_sessions}**")
            st.markdown(f"**Activity:** {st.session_state.pomodoro_activity}")
        
        with col2:
            if st.button("⏹️ Stop Pomodoro", use_container_width=True):
                # Add partial time entry if work session was in progress
                if not is_break:
                    elapsed_work_minutes = elapsed_time.total_seconds() / 60
                    work_hours = elapsed_work_minutes / 60
                    
                    # Find activity ID
                    activity_id = None
                    for activity in activities:
                        if activity['name'] == st.session_state.pomodoro_activity:
                            activity_id = activity['id']
                            break
                    
                    if activity_id and work_hours > 0:
                        add_time_entry(
                            activity_id=activity_id,
                            hours=work_hours,
                            date=datetime.now(),
                            notes=f"Partial Pomodoro session: {elapsed_work_minutes:.1f} minutes"
                        )
                
                st.session_state.pomodoro_running = False
                st.success("Pomodoro stopped")
                st.rerun()
        
        # Auto-refresh
        time.sleep(1)
        st.rerun()

# Quick time entries
st.markdown("---")
st.subheader("⚡ Quick Time Entries")

quick_times = [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
cols = st.columns(len(quick_times))

for i, quick_time in enumerate(quick_times):
    with cols[i]:
        if st.button(f"{quick_time}h", use_container_width=True):
            st.session_state.quick_time = quick_time
            st.session_state.show_quick_entry = True

if st.session_state.get('show_quick_entry', False):
    st.markdown("### Add Quick Entry")
    
    with st.form("quick_entry"):
        col1, col2 = st.columns(2)
        
        with col1:
            activity_names = [activity['name'] for activity in activities]
            quick_activity = st.selectbox("Activity", activity_names, key="quick_activity")
        
        with col2:
            quick_date = st.date_input("Date", datetime.now(), key="quick_date")
        
        quick_notes = st.text_input("Notes", key="quick_notes")
        
        col_add, col_cancel = st.columns(2)
        
        with col_add:
            if st.form_submit_button("Add Entry"):
                # Find activity ID
                activity_id = None
                for activity in activities:
                    if activity['name'] == quick_activity:
                        activity_id = activity['id']
                        break
                
                if activity_id:
                    success = add_time_entry(
                        activity_id=activity_id,
                        hours=st.session_state.quick_time,
                        date=datetime.combine(quick_date, datetime.min.time()),
                        notes=quick_notes
                    )
                    
                    if success:
                        st.success(f"✅ Added {st.session_state.quick_time} hours to {quick_activity}")
                        st.session_state.show_quick_entry = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to add time entry")
        
        with col_cancel:
            if st.form_submit_button("Cancel"):
                st.session_state.show_quick_entry = False
                st.rerun()

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("📊 Statistics", use_container_width=True):
        st.switch_page("pages/2_📊_Statistics.py")

with col3:
    if st.button("🎯 Activities", use_container_width=True):
        st.switch_page("pages/3_🎯_Activities.py") 