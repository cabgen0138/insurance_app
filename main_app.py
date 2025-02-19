import streamlit as st
from pages.account_info import render_step1
from pages.document_selection import render_step2

def main():
    st.set_page_config(
        page_title="Insurance Submission Clearance",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("Insurance Submission Clearance")
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state['step'] = 1
    
    # Render appropriate step
    if st.session_state.step == 1:
        render_step1()
    elif st.session_state.step == 2:
        render_step2()

if __name__ == "__main__":
    main()