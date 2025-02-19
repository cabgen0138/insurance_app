import streamlit as st
from datetime import datetime, date
from models import DocumentSubmission
from config import (
    REQUIRED_DOCS, DECLINE_REASONS, BASIC_REQUIRED_DOCS,
    BASE_ADDITIONAL_DOCS
)
from email_generators import (
    generate_declined_email,
    generate_not_cleared_email,
    generate_reserved_email
)
from main_app import add_to_history

def get_pipeline_data(
    effective_date: date,
    association_name: str,
    agency: str,
    region: str,
    stories: int,
    year_built: int,
    tiv: float,
    submission_status: str
) -> str:
    """
    Format data for pipeline spreadsheet in a tab-separated format
    """
    # Determine status based on submission outcome
    if submission_status == "Not Cleared - RFI":
        pipeline_status = "Not Cleared - RFI"
    elif submission_status == "Reserved":
        pipeline_status = "Reserved - Pending Setup"
    elif submission_status == "Not Cleared - OOA":
        pipeline_status = "Not Cleared - OOA"
    else:
        pipeline_status = ""

    # Format TIV with commas and no decimals
    formatted_tiv = f"${tiv:,.0f}"
    
    # Create tab-separated string with all fields
    pipeline_data = [
        effective_date.strftime("%m/%d/%Y"),  # Effective Date
        association_name,                      # Insured
        agency,                               # Agent (matches dropdown)
        region,                               # Region (matches dropdown)
        str(stories),                         # # Stories
        "",                                   # Type (skip)
        str(year_built),                      # Year Built
        formatted_tiv,                        # TIV
        "",                                   # Premium (skip)
        "",                                   # Rate (skip)
        "",                                   # Pr(Bind) (skip)
        "",                                   # Carrier (skip)
        "",                                   # Underwriter
        "",                                   # Need By
        pipeline_status                       # Status (matches dropdown)
    ]
    
    return "\t".join(pipeline_data)

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
    """
    Filter available loss run years based on year built
    """
    current_year = datetime.today().year
    all_years = []
    start_year = max(2020, year_built)  # Don't go earlier than 2020 or building construction
    
    while start_year < current_year:
        all_years.append(f"Loss Runs {start_year}-{start_year + 1}")
        start_year += 1
    
    return all_years

def render_step2():
    """Render the second step of the submission process"""
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
        st.subheader("Required Documents")
        
        # Basic required documents
        basic_docs = {doc: st.checkbox(doc) for doc in BASIC_REQUIRED_DOCS}
        
        # Check if Supplemental Application is received
        has_supplemental = basic_docs.get("Supplemental Application", False)

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
        
         # Combine required docs
        received_docs = {**basic_docs, **loss_run_docs}
        
        # Additional Documents section
        st.subheader("Additional Documents")
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
    
    # Handle pipeline button click
    if pipeline_button:
        # Determine current status
        if 'submission_status' in st.session_state:
            status = st.session_state.submission_status
        else:
            status = "Not Cleared - RFI"  # Default status
            
        # Generate pipeline data
        pipeline_data = get_pipeline_data(
            effective_date=st.session_state.effective_date,
            association_name=st.session_state.association_name,
            agency=st.session_state.agency,
            region=st.session_state.region,
            stories=st.session_state.stories,
            year_built=st.session_state.year_built,
            tiv=st.session_state.tiv,
            submission_status=status
        )
        
        # Display the data in a copyable text input
        st.text_input(
            "Pipeline Data (Click to select, then Ctrl+C to copy)",
            value=pipeline_data,
            key="pipeline_copy_field"
        )
    
    # Handle other button clicks
    if back_button:
        st.session_state.step = 1
        st.rerun()
    
    elif decline_button:
        st.session_state.showing_decline_reasons = True
    
    elif submit_button:
        doc_submission = DocumentSubmission(
            required_docs=received_docs,
            additional_docs=received_additional_docs
        )
        
        # Check for missing Acord and SOV
        if not received_docs.get("Acord 125/140") or not received_docs.get("SOV"):
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
                required_docs=received_docs
            )
            st.error("### Submission Outcome: Declined")
            st.text_area("Generated Email", email_body, height=400)
            st.session_state.submission_status = "Declined"
        else:
            # Determine submission outcome
            if doc_submission.is_complete():
                outcome = "Reserved"
            elif st.session_state.year_built >= 1980:
                outcome = "Not Cleared - RFI"
            else:
                outcome = "Not Cleared - OOA"
            
            st.session_state.submission_status = outcome
            
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
            
            st.text_area("Generated Email", email_body, height=400)
    
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
            st.session_state.submission_status = "Declined"
        else:
            st.warning("Please select at least one decline reason")