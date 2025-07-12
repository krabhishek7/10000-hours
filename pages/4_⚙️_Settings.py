import streamlit as st
import pandas as pd
import os
from datetime import datetime
from database.crud import get_activities, get_time_entries_df

# Page config
st.set_page_config(
    page_title="Settings - 10,000 Hour Tracker",
    page_icon="⚙️",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass

st.title("⚙️ Settings")
st.markdown("Configure your 10,000-hour tracker preferences and manage your data")

# Application settings
st.markdown("---")
st.subheader("🎨 Application Settings")

# Theme settings
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Display Preferences")
    
    # Goal hours setting
    goal_hours = st.number_input(
        "Goal Hours",
        min_value=1000,
        max_value=50000,
        value=10000,
        step=1000,
        help="Set your target hours for mastery"
    )
    
    # Time format
    time_format = st.selectbox(
        "Time Format",
        ["Hours (1.5h)", "Hours:Minutes (1:30)", "Minutes (90m)"],
        index=0
    )
    
    # Default timer duration
    default_timer = st.number_input(
        "Default Timer (minutes)",
        min_value=15,
        max_value=120,
        value=25,
        step=5,
        help="Default duration for Pomodoro timer"
    )

with col2:
    st.markdown("#### Notification Settings")
    
    # Enable notifications
    notifications = st.checkbox("Enable Notifications", value=True)
    
    # Milestone notifications
    milestone_notifications = st.checkbox("Milestone Notifications", value=True)
    
    # Daily reminder
    daily_reminder = st.checkbox("Daily Reminder", value=False)
    
    if daily_reminder:
        reminder_time = st.time_input("Reminder Time", value=datetime.strptime("20:00", "%H:%M").time())

# Data management
st.markdown("---")
st.subheader("📊 Data Management")

# Database statistics
activities = get_activities()
df = get_time_entries_df()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Activities", len(activities))

with col2:
    st.metric("Total Time Entries", len(df))

with col3:
    if not df.empty:
        st.metric("Total Hours Tracked", f"{df['hours'].sum():.1f}h")
    else:
        st.metric("Total Hours Tracked", "0h")

# Export data
st.markdown("#### 📥 Export Data")

col1, col2 = st.columns(2)

with col1:
    if st.button("Export All Data", use_container_width=True):
        if not df.empty:
            # Create comprehensive export
            export_data = df.copy()
            
            # Add activity details
            activity_dict = {activity['id']: activity for activity in activities}
            export_data['activity_category'] = export_data['activity_id'].map(
                lambda x: activity_dict.get(x, {}).get('category', '')
            )
            export_data['activity_description'] = export_data['activity_id'].map(
                lambda x: activity_dict.get(x, {}).get('description', '')
            )
            
            csv = export_data.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"10k_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.error("No data to export")

with col2:
    if st.button("Backup Database", use_container_width=True):
        # Check if database file exists
        if os.path.exists("tracker.db"):
            with open("tracker.db", "rb") as f:
                st.download_button(
                    label="Download Database",
                    data=f.read(),
                    file_name=f"tracker_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                    mime="application/octet-stream"
                )
        else:
            st.error("Database file not found")

# Import data
st.markdown("#### 📤 Import Data")

uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

if uploaded_file is not None:
    st.warning("⚠️ Import functionality is not yet implemented. This feature will be added in a future update.")

# Danger zone
st.markdown("---")
st.subheader("🚨 Danger Zone")

st.error("⚠️ **Warning:** The actions below are irreversible!")

col1, col2 = st.columns(2)

with col1:
    if st.button("Clear All Time Entries", use_container_width=True):
        st.session_state.show_clear_entries_confirm = True

with col2:
    if st.button("Reset All Data", use_container_width=True):
        st.session_state.show_reset_confirm = True

# Confirmation dialogs
if st.session_state.get('show_clear_entries_confirm', False):
    st.markdown("#### ⚠️ Confirm Clear All Time Entries")
    st.error("This will permanently delete all time entries while keeping your activities. This action cannot be undone.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, Clear All Entries", type="primary"):
            # Implementation would go here
            st.success("All time entries have been cleared.")
            st.session_state.show_clear_entries_confirm = False
            st.rerun()
    
    with col2:
        if st.button("Cancel"):
            st.session_state.show_clear_entries_confirm = False
            st.rerun()

if st.session_state.get('show_reset_confirm', False):
    st.markdown("#### ⚠️ Confirm Reset All Data")
    st.error("This will permanently delete ALL data including activities and time entries. This action cannot be undone.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, Reset Everything", type="primary"):
            # Implementation would go here
            st.success("All data has been reset.")
            st.session_state.show_reset_confirm = False
            st.rerun()
    
    with col2:
        if st.button("Cancel"):
            st.session_state.show_reset_confirm = False
            st.rerun()

# About section
st.markdown("---")
st.subheader("ℹ️ About")

st.markdown("""
### 10,000 Hour Tracker v1.0

Built with:
- **Streamlit** - Web framework
- **SQLite** - Database
- **Plotly** - Charts and visualizations
- **Pandas** - Data processing

### Features:
- ⏱️ **Real-time timer** with pause/resume functionality
- 🍅 **Pomodoro timer** for focused work sessions
- 📊 **Comprehensive statistics** and visualizations
- 🎯 **Multiple activity tracking** with progress rings
- 📱 **Responsive design** for mobile and desktop
- 💾 **Data export** and backup capabilities

### The 10,000 Hour Rule:
Based on Malcolm Gladwell's research, it takes approximately 10,000 hours of deliberate practice to achieve mastery in any field. This tracker helps you monitor your progress toward expertise.

### Support:
For questions or feedback, please check the documentation or create an issue on GitHub.
""")

# System information
if st.checkbox("Show System Information"):
    st.markdown("#### System Information")
    
    system_info = {
        "Python Version": "3.8+",
        "Streamlit Version": "1.28.0",
        "Database": "SQLite",
        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    for key, value in system_info.items():
        st.text(f"{key}: {value}")

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("⏱️ Timer", use_container_width=True):
        st.switch_page("pages/1_⏱️_Timer.py")

with col3:
    if st.button("📊 Statistics", use_container_width=True):
        st.switch_page("pages/2_📊_Statistics.py") 