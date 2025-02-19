import streamlit as st
from datetime import datetime

def initialize_history():
    """Initialize submission history in session state if it doesn't exist"""
    if 'submission_history' not in st.session_state:
        st.session_state.submission_history = []

def clear_submission_data():
    """Clear all submission-related data from session state while preserving history"""
    # Get current history
    current_history = st.session_state.get('submission_history', [])
    
    # List of all submission-related keys we want to clear
    submission_keys = [
        'step',
        'effective_date',
        'association_name',
        'agency',
        'county',
        'region',
        'year_built',
        'roof_replacement',
        'stories',
        'tiv',
        'construction_type',
        'outdoor_property_tiv',
        'showing_decline_reasons',
        'needs_referral',
        'submission_status'
    ]
    
    # Clear only submission-related keys
    for key in submission_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset step to 1
    st.session_state.step = 1
    
    # Restore history
    st.session_state.submission_history = current_history

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