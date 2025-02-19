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

def render_sidebar():
    """Render the sidebar with submission inbox and search"""
    with st.sidebar:
        # New Submission button at the top
        if st.button("🆕 New Submission", use_container_width=True):
            clear_submission_data()
            st.rerun()
            
        # Search bar
        st.text_input("🔍 Search by name...", placeholder="Search associations...", key="search_name")
        
        # Filters section
        st.markdown("### Filters")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("From Date", key="filter_date_from")
        with col2:
            st.date_input("To Date", key="filter_date_to")
            
        # Status filter
        status_filter = st.multiselect(
            "Status",
            ["New", "In Progress", "Reserved", "Not Cleared - RFI", "Not Cleared - OOA", "Declined", "Referred"],
            default=["New"]
        )
        
        # Agency filter
        agency_filter = st.multiselect(
            "Agency",
            ["Acentria - Port St Lucie", "Brown & Brown - Sarasota", "CBIZ Insurance", 
             "AP - Lake Mary", "USI - Tampa"],  # Sample agencies
            default=[]
        )
        
        # Region filter
        region_filter = st.multiselect(
            "Region",
            ["Big Bend", "Northeast", "Panhandle", "Space Coast", "Tri-County", 
             "Southwest", "Tampa/St Pete", "Central"],
            default=[]
        )
        
        # TIV Range filter
        st.select_slider(
            "TIV Range",
            options=["$5M-$20M", "$20M-$40M", "$40M-$60M", "$60M-$80M", "$80M-$100M", "Over $100M"],
            value=("$5M-$20M", "Over $100M")
        )
        
        # Sort options
        st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Association Name (A-Z)", "Agency Name (A-Z)", "TIV (High-Low)"]
        )
        
        # Submissions List
        st.markdown("### Submission Inbox")
        
        # Sample inbox data (this would come from database)
        sample_submissions = [
            {
                'date': '02/19/2025',
                'timestamp': '10:30 AM',
                'association': 'Ocean View Condos',
                'agency': 'Brown & Brown - Sarasota',
                'status': 'New',
                'region': 'Southwest',
                'tiv': '$25M',
                'unread': True
            },
            {
                'date': '02/19/2025',
                'timestamp': '10:15 AM',
                'association': 'Sunset Gardens HOA',
                'agency': 'CBIZ Insurance',
                'status': 'In Progress',
                'region': 'Central',
                'tiv': '$12M',
                'unread': False
            },
            {
                'date': '02/19/2025',
                'timestamp': '9:45 AM',
                'association': 'Lakeside Manor',
                'agency': 'AP - Lake Mary',
                'status': 'New',
                'region': 'Northeast',
                'tiv': '$45M',
                'unread': True
            }
        ]

        # Display submissions
        for submission in sample_submissions:
            with st.container():
                # Status color indicators
                status_colors = {
                    'New': '🔵',
                    'In Progress': '🟡',
                    'Reserved': '🟢',
                    'Not Cleared - RFI': '🟠',
                    'Not Cleared - OOA': '🟠',
                    'Declined': '🔴',
                    'Referred': '🟣'
                }
                
                status_icon = status_colors.get(submission['status'], '⚪')
                
                # Create a clickable container for each submission
                if st.button(
                    f"""{status_icon} **{submission['association']}**
                    {submission['date']} - {submission['timestamp']}
                    {submission['agency']}
                    Region: {submission['region']} | TIV: {submission['tiv']}
                    Status: *{submission['status']}*""",
                    key=f"submission_{submission['association']}",
                    use_container_width=True
                ):
                    # This would load the submission data into the main view
                    st.session_state.update({
                        'selected_submission': submission['association']
                    })
                st.markdown("---")

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
    
    # Render the sidebar
    render_sidebar()
    
    # Main content
    st.title("Cabrillo Submission Clearance")
    
    # Render appropriate step
    if st.session_state.step == 1:
        render_step1()
    elif st.session_state.step == 2:
        render_step2()

if __name__ == "__main__":
    main()