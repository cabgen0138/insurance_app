import streamlit as st
from datetime import datetime
from pages.account_info import render_step1
from pages.document_selection import render_step2
from utils.history_manager import initialize_history, clear_submission_data

def initialize_history():
    """Initialize submission history in session state if it doesn't exist"""
    if 'submission_history' not in st.session_state:
        st.session_state.submission_history = []

def clear_submission_data():
    """Clear all submission-related data from session state"""
    # List of keys to preserve
    keys_to_keep = ['submission_history']
    
    # Store values of keys we want to keep
    preserved_values = {key: st.session_state[key] for key in keys_to_keep if key in st.session_state}
    
    # Clear session state
    st.session_state.clear()
    
    # Restore preserved values
    for key, value in preserved_values.items():
        st.session_state[key] = value
    
    # Reset step to 1
    st.session_state.step = 1

def add_to_history(association_name, agency, status):
    """Add a submission to the history"""
    if 'submission_history' not in st.session_state:
        st.session_state.submission_history = []
    
    submission = {
        'timestamp': datetime.now().strftime('%I:%M %p'),
        'association': association_name,
        'agency': agency,
        'status': status
    }
    
    st.session_state.submission_history.append(submission)

def main():
    st.set_page_config(
        page_title="Cabrillo Submission Clearance",
        page_icon="📋",
        layout="wide"
    )
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    initialize_history()
        
    # Main content
    st.title("Cabrillo Submission Clearance")
    
    # Render appropriate step
    if st.session_state.step == 1:
        render_step1()
    elif st.session_state.step == 2:
        render_step2()

if __name__ == "__main__":
    main()