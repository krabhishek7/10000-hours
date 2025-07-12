import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
from database.crud import get_activities, get_main_activity, add_time_entry, add_activity
from components.timer import timer
from components.progress_ring import create_progress_ring
from utils.time_helpers import format_duration, estimate_completion_date

st.set_page_config(
    page_title="10,000 Hour Tracker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = 0

def main():
    st.markdown("""
        <div class="main-header floating-element">
            <h1>🎯 10,000 Hour Mastery Tracker</h1>
            <p>Track your journey to expertise, one hour at a time</p>
            <div style="margin-top: 1rem; font-size: 0.875rem; opacity: 0.8;">
                ✨ Deliberate practice leads to mastery ✨
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    activities = get_activities()
    
    if not activities:
        st.warning("⚠️ No activities found. Please add an activity to get started!")
        
        st.subheader("🚀 Quick Setup")
        with st.form("quick_setup"):
            col1, col2 = st.columns(2)
            with col1:
                activity_name = st.text_input("Activity Name", placeholder="e.g., Python Programming")
            with col2:
                activity_category = st.text_input("Category", placeholder="e.g., Programming")
            
            activity_description = st.text_area("Description (optional)", placeholder="Describe your learning goal...")
            
            submitted = st.form_submit_button("Create Activity", use_container_width=True)
            
            if submitted and activity_name:
                activity_id = add_activity(
                    name=activity_name,
                    description=activity_description,
                    category=activity_category,
                    is_main=True
                )
                if activity_id:
                    st.success(f"✅ Activity '{activity_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create activity. Please try again.")
        
        return
    
    main_activity = get_main_activity()
    
    if main_activity:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown("### 📊 Today's Stats")
            
            st.metric(
                label="Hours Today",
                value=f"{main_activity['today_hours']:.1f}h",
                delta=f"+{main_activity['today_hours']:.1f}h"
            )
            
            st.metric(
                label="This Week",
                value=f"{main_activity['week_hours']:.1f}h",
                delta=f"+{main_activity['week_hours'] - main_activity['today_hours']:.1f}h"
            )
            
            st.metric(
                label="Total Hours",
                value=f"{main_activity['total_hours']:.1f}h",
                delta=f"{(main_activity['total_hours']/10000*100):.1f}%"
            )
            
            if timer.is_running():
                st.markdown("---")
                st.markdown("### ⏱️ Current Timer")
                elapsed = timer.get_elapsed_time()
                time_details = timer.format_time_detailed(elapsed)
                
                status = "⏸️ PAUSED" if st.session_state.get('is_paused', False) else "⏱️ RUNNING"
                
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(74, 222, 128, 0.1) 100%);
                        border: 2px solid var(--primary-color);
                        border-radius: 12px;
                        padding: 1rem;
                        text-align: center;
                        margin: 1rem 0;
                    ">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">{status}</div>
                        <div style="display: flex; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">{time_details['hours']:02d}</div>
                                <div style="font-size: 0.75rem; color: var(--text-secondary);">H</div>
                            </div>
                            <div style="font-size: 1.5rem; color: var(--text-secondary);">:</div>
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">{time_details['minutes']:02d}</div>
                                <div style="font-size: 0.75rem; color: var(--text-secondary);">M</div>
                            </div>
                            <div style="font-size: 1.5rem; color: var(--text-secondary);">:</div>
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">{time_details['seconds']:02d}</div>
                                <div style="font-size: 0.75rem; color: var(--text-secondary);">S</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                time.sleep(1)
                st.rerun()
        
        with col2:
            progress = (main_activity['total_hours'] / 10000) * 100
            fig = create_progress_ring(
                main_activity['total_hours'], 
                main_activity['name']
            )
            st.plotly_chart(fig, use_container_width=True, key="main_dashboard_chart")
            
            st.markdown("### 🎮 Timer Controls")
            timer_col1, timer_col2, timer_col3 = st.columns(3)
            
            with timer_col1:
                if st.button("▶️ Start Timer", 
                           use_container_width=True, 
                           disabled=timer.is_running(),
                           type="primary"):
                    if timer.start_timer(main_activity['id']):
                        st.success("✅ Timer started!")
                        st.rerun()
                    else:
                        st.error("❌ Timer is already running")
            
            with timer_col2:
                if timer.is_running():
                    if st.session_state.get('is_paused', False):
                        if st.button("▶️ Resume", use_container_width=True):
                            timer.resume_timer()
                            st.session_state.is_paused = False
                            st.rerun()
                    else:
                        if st.button("⏸️ Pause", use_container_width=True):
                            timer.pause_timer()
                            st.session_state.is_paused = True
                            st.rerun()
                else:
                    st.button("⏸️ Pause", use_container_width=True, disabled=True)
            
            with timer_col3:
                if st.button("⏹️ Stop Timer", 
                           use_container_width=True, 
                           disabled=not timer.is_running(),
                           type="secondary"):
                    hours_added = timer.stop_timer()
                    if hours_added > 0:
                        st.success(f"✅ Added {hours_added:.2f} hours to {main_activity['name']}")
                        st.session_state.is_paused = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to stop timer")
        
        with col3:
            st.markdown("### 🎯 Progress")
            
            progress_pct = (main_activity['total_hours'] / 10000) * 100
            st.metric(
                label="Progress",
                value=f"{progress_pct:.1f}%",
                delta=f"{progress_pct:.1f}%"
            )
            
            daily_avg = main_activity['daily_avg']
            st.metric(
                label="Daily Average",
                value=f"{daily_avg:.1f}h",
                delta=f"{daily_avg:.1f}h"
            )
            
            if daily_avg > 0:
                remaining_hours = 10000 - main_activity['total_hours']
                days_remaining = remaining_hours / daily_avg
                completion_date = datetime.now() + timedelta(days=days_remaining)
                
                if days_remaining < 365:
                    completion_text = f"{days_remaining:.0f} days"
                else:
                    completion_text = f"{days_remaining/365:.1f} years"
                
                st.metric(
                    label="Est. Completion",
                    value=completion_text,
                    delta=completion_date.strftime("%b %d, %Y")
                )
            else:
                st.metric(
                    label="Est. Completion",
                    value="N/A",
                    delta="Start tracking!"
                )
    
    st.markdown("---")
    st.subheader("📝 Manual Time Entry")
    
    with st.form("manual_entry"):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            activity_names = [activity['name'] for activity in activities]
            selected_activity = st.selectbox("Select Activity", activity_names)
        
        with col2:
            hours = st.number_input("Hours", min_value=0.0, max_value=24.0, step=0.25, value=1.0)
        
        with col3:
            date = st.date_input("Date", datetime.now())
        
        notes = st.text_area("Notes (optional)", placeholder="What did you work on?")
        
        submitted = st.form_submit_button("Add Entry", use_container_width=True)
        
        if submitted:
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
                    st.success(f"✅ Added {hours} hours to {selected_activity}")
                    st.rerun()
                else:
                    st.error("❌ Failed to add time entry")
    
    st.markdown("---")
    st.subheader("📚 All Activities")
    
    if len(activities) > 1:
        cols = st.columns(min(3, len(activities)))
        
        for i, activity in enumerate(activities):
            with cols[i % 3]:
                with st.expander(f"{activity['name']} - {activity['total_hours']:.1f}h"):
                    progress = min(activity['total_hours'] / 10000, 1.0)
                    st.progress(progress)
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Total", f"{activity['total_hours']:.1f}h")
                    with col_b:
                        st.metric("Sessions", activity['session_count'])
                    with col_c:
                        st.metric("Streak", f"{activity['streak']} days")
                    
                    if activity['description']:
                        st.markdown(f"*{activity['description']}*")
                    
                    if activity['category']:
                        st.markdown(f"**Category:** {activity['category']}")
                    
                    if activity['is_main']:
                        st.markdown("⭐ **Main Activity**")
    else:
        st.info("💡 Add more activities to see them here!")
    
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add New Activity", use_container_width=True):
            st.session_state.show_add_activity = True
    
    with col2:
        if st.button("📊 View Statistics", use_container_width=True):
            st.switch_page("pages/2_📊_Statistics.py")
    
    with col3:
        if st.button("⏱️ Timer Page", use_container_width=True):
            st.switch_page("pages/1_⏱️_Timer.py")
    
    if st.session_state.get('show_add_activity', False):
        st.markdown("---")
        st.subheader("➕ Add New Activity")
        
        with st.form("add_activity"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Activity Name", placeholder="e.g., Machine Learning")
                new_category = st.text_input("Category", placeholder="e.g., Data Science")
            
            with col2:
                color = st.color_picker("Color", "#3B82F6")
                is_main = st.checkbox("Set as Main Activity")
            
            new_description = st.text_area("Description", placeholder="Describe your learning goal...")
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submitted = st.form_submit_button("Create Activity", use_container_width=True)
            
            with col_cancel:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)
            
            if submitted and new_name:
                activity_id = add_activity(
                    name=new_name,
                    description=new_description,
                    category=new_category,
                    is_main=is_main,
                    color=color
                )
                
                if activity_id:
                    st.success(f"✅ Activity '{new_name}' created successfully!")
                    st.session_state.show_add_activity = False
                    st.rerun()
                else:
                    st.error("❌ Failed to create activity")
            
            if cancelled:
                st.session_state.show_add_activity = False
                st.rerun()

if __name__ == "__main__":
    main() 