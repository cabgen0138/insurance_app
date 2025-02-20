import streamlit as st
from datetime import datetime
from models import DocumentSubmission
from config import (
    REQUIRED_DOCS, DECLINE_REASONS, BASIC_REQUIRED_DOCS,
    BASE_ADDITIONAL_DOCS, get_pipeline_data
)
from email_generators import (
    generate_declined_email,
    generate_not_cleared_email,
    generate_reserved_email
)
from utils.history_manager import add_to_history

def get_additional_docs(has_supplemental: bool = False) -> list:
    """
    Determine which additional documents are needed based on property characteristics
    Args:
        has_supplemental: Boolean indicating if Supplemental Application was received
    Returns:
        list: List of tuples (doc_name, description)
    """
    current_year = datetime.today().year
    applicable_docs = []
    
    # Add base docs excluding Engineer Inspection and Prior Claims Experience
    for doc_name, description in BASE_ADDITIONAL_DOCS:
        if doc_name not in ["Engineer Inspection", "Prior Claims Experience"]:
            applicable_docs.append((doc_name, description))
    
    # Only add Engineer Inspection and Prior Claims Experience if supplemental is received
    if has_supplemental:
        applicable_docs.extend([
            doc for doc in BASE_ADDITIONAL_DOCS 
            if doc[0] in ["Engineer Inspection", "Prior Claims Experience"]
        ])
    
    # Association Documents logic
    association_name = st.session_state.association_name.lower()
    if not any(term in association_name for term in ['condo', 'condominium']):
        applicable_docs.append(
            ("Association Documents", "Declarations and Bylaws")
        )
    
    # Additional Loss History logic
    if st.session_state.year_built <= 2017:
        applicable_docs.append(
            ("Additional Loss History", "2017-2020 loss runs, if available")
        )
    
    # Structural Inspection logic
    if (st.session_state.stories >= 3 and 
        (current_year - st.session_state.year_built) >= 25):
        applicable_docs.append(
            ("Structural Inspection", "Most recent structural or milestone inspection")
        )
    
    # Building Updates logic
    if (current_year - st.session_state.year_built) >= 40:
        applicable_docs.append(
            ("Building Updates", "Provide documentation confirming the condition, type, and history of any updates to wiring and plumbing systems")
        )
    
    # Roof Condition logic
    if (current_year - st.session_state.roof_replacement) >= 15:
        applicable_docs.append(
            ("Roof Condition Inspection", "Provide a current roof condition inspection for all roofs that are 15+ years old")
        )
    
    return applicable_docs

def filter_loss_run_years(year_built: int) -> list:
    """Filter available loss run years based on year built"""
    current_year = datetime.today().year
    all_years = []
    start_year = max(2020, year_built)
    
    while start_year < current_year:
        all_years.append(f"Loss Runs {start_year}-{start_year + 1}")
        start_year += 1
    
    return all_years

def render_step2():
    """Render the second step of the submission process"""
    # Initialize state for showing additional documents
    if 'showing_additional_docs' not in st.session_state:
        st.session_state.showing_additional_docs = False
    
    # Display summary of entered information
    st.subheader("Submission Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Association:** {st.session_state.association_name}")
        st.write(f"**Agency:** {st.session_state.agency}")
        st.write(f"**County:** {st.session_state.county}")
        st.write(f"**Region:** {st.session_state.region}")
        st.write(f"**Construction Type:** {st.session_state.construction_type}")
        
    with col2:
        st.write(f"**Year Built:** {st.session_state.year_built}")
        st.write(f"**Roof Replacement:** {st.session_state.roof_replacement}")
        st.write(f"**Stories:** {st.session_state.stories}")
        st.write(f"**TIV:** ${st.session_state.tiv:,.2f}")
    
    # Document selection form
    with st.form("document_selection_form"):
        if not st.session_state.showing_additional_docs:
            # Step 1: Initial Documents
            st.subheader("Required Documents")
            
            # Basic required documents
            basic_docs = {doc: st.checkbox(doc) for doc in BASIC_REQUIRED_DOCS}
            
            # Loss Runs section
            st.subheader("Loss Runs")
            available_loss_runs = filter_loss_run_years(st.session_state.year_built)
            loss_run_docs = {}
            
            if available_loss_runs:
                col1, col2 = st.columns(2)
                mid_point = len(available_loss_runs) // 2
                
                with col1:
                    for year in available_loss_runs[:mid_point]:
                        loss_run_docs[year] = st.checkbox(year)
                with col2:
                    for year in available_loss_runs[mid_point:]:
                        loss_run_docs[year] = st.checkbox(year)
                        
            # Continue button
            continue_button = st.form_submit_button("Continue to Additional Documents")
            
            if continue_button:
                # Store selections in session state
                st.session_state.basic_docs = basic_docs
                st.session_state.loss_run_docs = loss_run_docs
                st.session_state.showing_additional_docs = True
                st.rerun()
                
        else:
            # Step 2: Show selected documents and additional documents
            st.subheader("Selected Documents")
            
            # Display which initial documents were selected
            st.write("Initial documents received:")
            for doc, received in st.session_state.basic_docs.items():
                if received:
                    st.write(f"- {doc}")
            
            for doc, received in st.session_state.loss_run_docs.items():
                if received:
                    st.write(f"- {doc}")
            
            st.markdown("---")
            
            # Additional Documents section
            st.subheader("Additional Documents")
            has_supplemental = st.session_state.basic_docs.get("Supplemental Application", False)
            additional_docs = get_additional_docs(has_supplemental)
            received_additional_docs = {}
            
            for doc_name, description in additional_docs:
                if description:
                    label = f"{doc_name}: {description}"
                else:
                    label = doc_name
                received_additional_docs[label] = st.checkbox(label)
            
            # Form buttons
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                back_button = st.form_submit_button("Back")
            
            with col2:
                decline_button = st.form_submit_button("Decline")
                
            with col3:
                submit_button = st.form_submit_button("Submit")

            with col4:
                pipeline_button = st.form_submit_button("Copy Pipeline Data")

            # Handle form submission
            if back_button:
                st.session_state.showing_additional_docs = False
                st.session_state.step = 1
                st.rerun()
            
            elif decline_button:
                st.session_state.showing_decline_reasons = True
            
            elif submit_button:
                # Combine all documents
                received_docs = {**st.session_state.basic_docs, **st.session_state.loss_run_docs}
                
                doc_submission = DocumentSubmission(
                    required_docs=received_docs,
                    additional_docs=received_additional_docs
                )
                
                # Determine submission outcome
                if doc_submission.is_complete():
                    outcome = "Reserved"
                elif st.session_state.year_built >= 1980:
                    outcome = "Not Cleared - RFI"
                else:
                    outcome = "Not Cleared - OOA"
                
                # Generate appropriate email
                if outcome == "Reserved":
                    email_body = generate_reserved_email(
                        association_name=st.session_state.association_name,
                        agency=st.session_state.agency,
                        year_built=st.session_state.year_built,
                        roof_replacement=st.session_state.roof_replacement,
                        stories=st.session_state.stories,
                        county=st.session_state.county,
                        received_docs=received_docs,
                        received_additional_docs=received_additional_docs,
                        effective_date=st.session_state.effective_date
                    )
                    st.success("### Submission Outcome: Reserved")
                    add_to_history(st.session_state.association_name, st.session_state.agency, "Reserved")
                else:
                    email_body = generate_not_cleared_email(
                        association_name=st.session_state.association_name,
                        agency=st.session_state.agency,
                        year_built=st.session_state.year_built,
                        roof_replacement=st.session_state.roof_replacement,
                        stories=st.session_state.stories,
                        county=st.session_state.county,
                        received_docs=received_docs,
                        received_additional_docs=received_additional_docs
                    )
                    st.warning(f"### Submission Outcome: {outcome}")
                    add_to_history(st.session_state.association_name, st.session_state.agency, outcome)
                
                st.text_area("Generated Email", email_body, height=400)
                
                # Generate and display pipeline data
                pipeline_data = get_pipeline_data(
                    effective_date=st.session_state.effective_date,
                    association_name=st.session_state.association_name,
                    agency=st.session_state.agency,
                    region=st.session_state.region,
                    stories=st.session_state.stories,
                    year_built=st.session_state.year_built,
                    tiv=st.session_state.tiv,
                    submission_status=outcome
                )
                
                st.text_input(
                    "Pipeline Data (Click to select, then Ctrl+C to copy)",
                    value=pipeline_data,
                    key="pipeline_copy_field"
                )
    
    # Show decline reasons selection if needed
    if st.session_state.showing_decline_reasons:
        show_decline_reasons_selection()

def show_decline_reasons_selection():
    """Show the decline reasons selection interface"""
    st.subheader("Select Declination Reason(s)")
    
    selected_reasons = []
    for key, value in DECLINE_REASONS.items():
        if st.checkbox(key, key=f"step2_{key}"):
            selected_reasons.append(value)
    
    if st.button("Generate Decline Email", key="step2_decline"):
        if selected_reasons:
            email_body = generate_declined_email(
                association_name=st.session_state.association_name,
                agency=st.session_state.agency,
                year_built=st.session_state.year_built,
                roof_replacement=st.session_state.roof_replacement,
                stories=st.session_state.stories,
                construction_type=st.session_state.construction_type,
                tiv=st.session_state.tiv,
                outdoor_property_tiv=st.session_state.outdoor_property_tiv,
                effective_date=st.session_state.effective_date,
                required_docs={},
                selected_reasons=selected_reasons
            )
            st.error("### Submission Outcome: Declined")
            st.text_area("Generated Email", email_body, height=400)
            st.session_state.showing_decline_reasons = False
            add_to_history(st.session_state.association_name, st.session_state.agency, "Declined")
        else:
            st.warning("Please select at least one decline reason")