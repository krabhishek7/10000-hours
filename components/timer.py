import streamlit as st
import time
from datetime import datetime, timedelta
from database.crud import add_time_entry

class Timer:
    def __init__(self):
        if 'timer_running' not in st.session_state:
            st.session_state.timer_running = False
        if 'start_time' not in st.session_state:
            st.session_state.start_time = None
        if 'current_activity_id' not in st.session_state:
            st.session_state.current_activity_id = None
        if 'elapsed_time' not in st.session_state:
            st.session_state.elapsed_time = timedelta(0)
        if 'paused_time' not in st.session_state:
            st.session_state.paused_time = timedelta(0)
        if 'is_paused' not in st.session_state:
            st.session_state.is_paused = False
    
    def start_timer(self, activity_id):
        if not st.session_state.timer_running:
            st.session_state.timer_running = True
            st.session_state.start_time = datetime.now()
            st.session_state.current_activity_id = activity_id
            st.session_state.elapsed_time = timedelta(0)
            st.session_state.paused_time = timedelta(0)
            st.session_state.is_paused = False
            return True
        return False
    
    def pause_timer(self):
        if st.session_state.timer_running and not st.session_state.is_paused:
            st.session_state.is_paused = True
            st.session_state.paused_time = datetime.now() - st.session_state.start_time
            return True
        return False
    
    def resume_timer(self):
        if st.session_state.timer_running and st.session_state.is_paused:
            st.session_state.is_paused = False
            st.session_state.start_time = datetime.now() - st.session_state.paused_time
            return True
        return False
    
    def stop_timer(self):
        if st.session_state.timer_running:
            if st.session_state.is_paused:
                elapsed = st.session_state.paused_time
            else:
                elapsed = datetime.now() - st.session_state.start_time
            
            hours = elapsed.total_seconds() / 3600
            
            success = add_time_entry(
                activity_id=st.session_state.current_activity_id,
                hours=hours,
                date=datetime.now()
            )
            
            st.session_state.timer_running = False
            st.session_state.start_time = None
            st.session_state.current_activity_id = None
            st.session_state.elapsed_time = timedelta(0)
            st.session_state.paused_time = timedelta(0)
            st.session_state.is_paused = False
            
            return hours if success else 0
        return 0
    
    def get_elapsed_time(self):
        if not st.session_state.timer_running:
            return timedelta(0)
        
        if st.session_state.is_paused:
            return st.session_state.paused_time
        else:
            return datetime.now() - st.session_state.start_time
    
    def format_time(self, td):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def format_time_detailed(self, td):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        }
    
    def display_timer(self):
        if st.session_state.timer_running:
            elapsed = self.get_elapsed_time()
            time_details = self.format_time_detailed(elapsed)
            
            status = "⏸️ PAUSED" if st.session_state.is_paused else "⏱️ RUNNING"
            status_class = "paused" if st.session_state.is_paused else "running"
            
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
            
            col1, col2 = st.columns(2)
            with col1:
                if st.session_state.is_paused:
                    if st.button("▶️ Resume", use_container_width=True, type="primary"):
                        self.resume_timer()
                        st.rerun()
                else:
                    if st.button("⏸️ Pause", use_container_width=True):
                        self.pause_timer()
                        st.rerun()
            with col2:
                if st.button("⏹️ Stop", use_container_width=True, type="secondary"):
                    hours_added = self.stop_timer()
                    if hours_added > 0:
                        st.success(f"✅ Session completed! Added {hours_added:.2f} hours")
                    st.rerun()
            
            return True
        return False
    
    def is_running(self):
        if 'timer_running' not in st.session_state:
            st.session_state.timer_running = False
        return st.session_state.timer_running
    
    def get_current_activity_id(self):
        if 'current_activity_id' not in st.session_state:
            st.session_state.current_activity_id = None
        return st.session_state.current_activity_id

def get_timer():
    if 'timer_instance' not in st.session_state:
        st.session_state.timer_instance = Timer()
    return st.session_state.timer_instance

timer = Timer() 