import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.crud import (
    get_activities, 
    add_activity, 
    update_activity, 
    delete_activity,
    get_time_entries_df,
    get_milestones
)
from components.progress_ring import create_mini_progress_ring, create_progress_ring
from utils.time_helpers import format_duration, estimate_completion_date

# Page config
st.set_page_config(
    page_title="Activities - 10,000 Hour Tracker",
    page_icon="🎯",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass

st.title("🎯 Activities")
st.markdown("Manage your learning activities and track your progress towards mastery")

# Get activities
activities = get_activities()

# Add new activity section
st.markdown("---")
st.subheader("➕ Add New Activity")

with st.form("add_activity"):
    col1, col2 = st.columns(2)
    
    with col1:
        activity_name = st.text_input("Activity Name", placeholder="e.g., Python Programming")
        activity_category = st.text_input("Category", placeholder="e.g., Programming")
        color = st.color_picker("Color", "#3B82F6")
    
    with col2:
        activity_description = st.text_area("Description", placeholder="Describe your learning goal...")
        is_main = st.checkbox("Set as Main Activity", help="The main activity will be featured prominently on the dashboard")
    
    submitted = st.form_submit_button("Create Activity", use_container_width=True)
    
    if submitted:
        if activity_name.strip():
            activity_id = add_activity(
                name=activity_name.strip(),
                description=activity_description.strip(),
                category=activity_category.strip(),
                is_main=is_main,
                color=color
            )
            
            if activity_id:
                st.success(f"✅ Activity '{activity_name}' created successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to create activity. Please try again.")
        else:
            st.error("❌ Please enter an activity name.")

# Activities management section
st.markdown("---")
st.subheader("📚 Manage Activities")

if not activities:
    st.info("🎯 No activities yet. Create your first activity above!")
else:
    # Activity overview cards
    st.markdown("### Activity Overview")
    
    # Create cards for each activity
    for i in range(0, len(activities), 3):
        cols = st.columns(3)
        
        for j, activity in enumerate(activities[i:i+3]):
            with cols[j]:
                with st.container():
                    # Activity card
                    st.markdown(f"""
                        <div class="activity-card">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <div style="width: 20px; height: 20px; background-color: {activity['color']}; border-radius: 50%; margin-right: 0.5rem;"></div>
                                <h4 style="margin: 0;">{activity['name']}</h4>
                                {'<span style="color: #F59E0B;">⭐ Main</span>' if activity['is_main'] else ''}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Progress ring
                    progress_ring = create_mini_progress_ring(
                        activity['total_hours'],
                        activity['name']
                    )
                    st.plotly_chart(progress_ring, use_container_width=True, key=f"activity_card_progress_{activity['id']}")
                    
                    # Stats
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Total Hours", f"{activity['total_hours']:.1f}h")
                        st.metric("Sessions", f"{activity['session_count']:,}")
                    with col_b:
                        st.metric("Daily Avg", f"{activity['daily_avg']:.1f}h")
                        st.metric("Streak", f"{activity['streak']} days")
                    
                    # Category and description
                    if activity['category']:
                        st.markdown(f"**Category:** {activity['category']}")
                    
                    if activity['description']:
                        st.markdown(f"*{activity['description']}*")
                    
                    # Action buttons
                    col_edit, col_delete = st.columns(2)
                    
                    with col_edit:
                        if st.button(f"✏️ Edit", key=f"edit_{activity['id']}", use_container_width=True):
                            st.session_state.edit_activity_id = activity['id']
                            st.session_state.show_edit_form = True
                    
                    with col_delete:
                        if st.button(f"🗑️ Delete", key=f"delete_{activity['id']}", use_container_width=True):
                            st.session_state.delete_activity_id = activity['id']
                            st.session_state.show_delete_confirm = True
    
    # Edit activity form
    if st.session_state.get('show_edit_form', False):
        edit_activity_id = st.session_state.get('edit_activity_id')
        edit_activity = None
        
        for activity in activities:
            if activity['id'] == edit_activity_id:
                edit_activity = activity
                break
        
        if edit_activity:
            st.markdown("---")
            st.subheader(f"✏️ Edit Activity: {edit_activity['name']}")
            
            with st.form("edit_activity"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Activity Name", value=edit_activity['name'])
                    new_category = st.text_input("Category", value=edit_activity['category'] or "")
                    new_color = st.color_picker("Color", value=edit_activity['color'])
                
                with col2:
                    new_description = st.text_area("Description", value=edit_activity['description'] or "")
                    new_is_main = st.checkbox("Set as Main Activity", value=edit_activity['is_main'])
                
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        success = update_activity(
                            activity_id=edit_activity_id,
                            name=new_name.strip(),
                            description=new_description.strip(),
                            category=new_category.strip(),
                            is_main=new_is_main,
                            color=new_color
                        )
                        
                        if success:
                            st.success(f"✅ Activity '{new_name}' updated successfully!")
                            st.session_state.show_edit_form = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to update activity.")
                
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_edit_form = False
                        st.rerun()
    
    # Delete confirmation
    if st.session_state.get('show_delete_confirm', False):
        delete_activity_id = st.session_state.get('delete_activity_id')
        activity_to_delete = None
        
        for activity in activities:
            if activity['id'] == delete_activity_id:
                activity_to_delete = activity
                break
        
        if activity_to_delete:
            st.markdown("---")
            st.error(f"⚠️ **Delete Activity: {activity_to_delete['name']}**")
            st.warning("This will permanently delete the activity and all its time entries. This action cannot be undone.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Yes, Delete", use_container_width=True, type="primary"):
                    success = delete_activity(delete_activity_id)
                    
                    if success:
                        st.success(f"✅ Activity '{activity_to_delete['name']}' deleted successfully!")
                        st.session_state.show_delete_confirm = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete activity.")
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_delete_confirm = False
                    st.rerun()
    
    # Detailed activity view
    st.markdown("---")
    st.subheader("📊 Detailed Activity View")
    
    # Activity selection
    activity_names = [activity['name'] for activity in activities]
    selected_activity_name = st.selectbox("Select Activity", activity_names)
    
    # Find selected activity
    selected_activity = None
    for activity in activities:
        if activity['name'] == selected_activity_name:
            selected_activity = activity
            break
    
    if selected_activity:
        # Activity details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {selected_activity['name']}")
            
            if selected_activity['description']:
                st.markdown(selected_activity['description'])
            
            # Metrics
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.metric("Total Hours", f"{selected_activity['total_hours']:.1f}h")
            
            with col_b:
                st.metric("Sessions", f"{selected_activity['session_count']:,}")
            
            with col_c:
                st.metric("Daily Average", f"{selected_activity['daily_avg']:.1f}h")
            
            with col_d:
                st.metric("Current Streak", f"{selected_activity['streak']} days")
            
            # Progress towards 10,000 hours
            progress_pct = (selected_activity['total_hours'] / 10000) * 100
            st.progress(progress_pct / 100)
            st.markdown(f"**Progress:** {progress_pct:.1f}% towards 10,000 hours")
            
            # Estimated completion
            if selected_activity['daily_avg'] > 0:
                remaining_hours = 10000 - selected_activity['total_hours']
                days_remaining = remaining_hours / selected_activity['daily_avg']
                completion_date = datetime.now() + timedelta(days=days_remaining)
                
                st.markdown(f"**Estimated Completion:** {completion_date.strftime('%B %d, %Y')} ({days_remaining:.0f} days)")
            else:
                st.markdown("**Estimated Completion:** Start tracking to see estimate")
        
        with col2:
            # Progress ring
            progress_ring = create_mini_progress_ring(
                selected_activity['total_hours'],
                selected_activity['name']
            )
            st.plotly_chart(progress_ring, use_container_width=True, key=f"progress_ring_{selected_activity['id']}")
        
        # Milestones
        st.markdown("#### 🏆 Milestones")
        
        milestones = [100, 500, 1000, 2500, 5000, 7500, 10000]
        current_hours = selected_activity['total_hours']
        
        milestone_cols = st.columns(len(milestones))
        
        for i, milestone in enumerate(milestones):
            with milestone_cols[i]:
                if current_hours >= milestone:
                    st.markdown(f"✅ **{milestone}h**")
                else:
                    remaining = milestone - current_hours
                    st.markdown(f"⏳ **{milestone}h**")
                    st.markdown(f"*{remaining:.1f}h to go*")
        
        # Recent activity
        st.markdown("#### 📈 Recent Activity")
        
        # Get recent time entries for this activity
        recent_df = get_time_entries_df()
        
        if not recent_df.empty:
            activity_df = recent_df[recent_df['activity_name'] == selected_activity['name']]
            
            if not activity_df.empty:
                # Show recent 10 entries
                recent_entries = activity_df.tail(10).sort_values('date', ascending=False)
                
                # Format for display
                display_entries = recent_entries[['date', 'hours', 'notes']].copy()
                display_entries['date'] = pd.to_datetime(display_entries['date']).dt.strftime('%Y-%m-%d')
                display_entries['hours'] = display_entries['hours'].apply(lambda x: f"{x:.2f}h")
                display_entries.columns = ['Date', 'Hours', 'Notes']
                
                st.dataframe(display_entries, use_container_width=True, hide_index=True)
                
                # Activity timeline chart
                st.markdown("#### 📊 Activity Timeline")
                
                # Group by date and sum hours
                daily_hours = activity_df.groupby('date')['hours'].sum().reset_index()
                daily_hours['date'] = pd.to_datetime(daily_hours['date'])
                
                import plotly.express as px
                
                fig = px.line(
                    daily_hours,
                    x='date',
                    y='hours',
                    title=f'{selected_activity["name"]} - Daily Hours',
                    markers=True
                )
                
                fig.update_traces(line_color=selected_activity['color'])
                fig.update_layout(
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"timeline_chart_{selected_activity['id']}")
            else:
                st.info(f"No time entries found for {selected_activity['name']}")
        else:
            st.info("No time entries found")

# Activity statistics
st.markdown("---")
st.subheader("📊 Activity Statistics")

if activities:
    # Summary statistics
    total_activities = len(activities)
    total_hours_all = sum(activity['total_hours'] for activity in activities)
    avg_hours_per_activity = total_hours_all / total_activities if total_activities > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Activities", total_activities)
    
    with col2:
        st.metric("Total Hours (All)", f"{total_hours_all:.1f}h")
    
    with col3:
        st.metric("Average per Activity", f"{avg_hours_per_activity:.1f}h")
    
    # Activity comparison chart
    st.markdown("#### Activity Comparison")
    
    activity_data = []
    for activity in activities:
        activity_data.append({
            'Activity': activity['name'],
            'Hours': activity['total_hours'],
            'Sessions': activity['session_count'],
            'Daily Average': activity['daily_avg']
        })
    
    comparison_df = pd.DataFrame(activity_data)
    
    import plotly.express as px
    
    fig = px.bar(
        comparison_df,
        x='Activity',
        y='Hours',
        title='Total Hours by Activity',
        color='Hours',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, key="activity_comparison_chart")

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