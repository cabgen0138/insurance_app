import streamlit as st
from datetime import datetime, timedelta
from models import PropertySubmission
from config import (AGENCIES, COUNTIES, CONSTRUCTION_TYPES, DECLINE_REASONS, get_region_for_county)
from email_generators.declined import generate_declined_email
from email_generators.referral import generate_referral_email
from utils.history_manager import add_to_history

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    defaults = {
        'effective_date': datetime.today(),
        'association_name': "",
        'agency': None,
        'county': None,
        'region': None,
        'year_built': 1900,
        'roof_replacement': 1900,
        'stories': 1,
        'tiv': 0.0,
        'construction_type': CONSTRUCTION_TYPES[0],
        'outdoor_property_tiv': 0.0,
        'showing_decline_reasons': False,
        'needs_referral': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def check_tiv_limits(tiv: float, stories: int) -> str:
    """
    Check TIV limits and return status
    Returns: 'decline', 'refer', or 'accept'
    """
    if tiv < 5_000_000:
        return 'decline'
    elif stories <= 3 and tiv > 60_000_000:  # Garden-style (1-3 stories)
        return 'decline'  # Changed from 'refer' to 'decline' for garden-style over limit
    elif tiv > 100_000_000:
        return 'refer'
    return 'accept'

def validate_submission(
    association_name: str,
    agency: str,
    year_built: int,
    roof_replacement: int,
    stories: int,
    construction_type: str,
    tiv: float,
    effective_date: datetime
) -> list:
    """
    Validates the submission and returns list of decline reasons if any
    """
    decline_reasons = []
    today = datetime.today()
    
    # Agency check
    if agency == "Unknown":
        decline_reasons.append("Agency Not Appointed")
    
    # Frame stories check
    if construction_type == "Frame" and stories > 5:
        decline_reasons.append(
            "Frame > 5 stories: The subject property includes predominantly "
            "frame building(s) > 5 stories."
        )
    
    # Effective date check
    if (effective_date - today.date()).days > 120:
        decline_reasons.append(
            "Effective Date: Requested effective date is > 120 days past "
            "the submission date; account cannot be reserved at this time."
        )
    
    # TIV checks - Primary validation
    if tiv < 5_000_000:
        decline_reasons.append("TIV < $5M: TIV is less than $5,000,000")
    elif stories <= 3 and tiv > 60_000_000:  # Garden-style (1-3 stories)
        decline_reasons.append(
            "Garden Style TIV > $60M: Per premises TIV exceeds $60M. We are generally "
            "looking for $5M-$60M TIVs for garden style risks (1-3 stories)."
        )
    elif tiv > 100_000_000:  # High-rise TIV check
        decline_reasons.append("TIV > $100M: Per premises TIV exceeds $100M")
    
    # Only add age-related decline reasons if there are TIV issues
    building_age = today.year - year_built
    roof_age = today.year - roof_replacement
    
    if decline_reasons:  # Only check ages if already declining for other reasons
        if building_age > 30:
            decline_reasons.append(
                "Building Age/Updates: Building age(s) exceeds 30 years and there is "
                "insufficient documentation confirming adequate building updates."
            )
        if roof_age > 15:
            decline_reasons.append(
                "Roof Age/Updates: Roof age(s) exceeds 15 years and there is "
                "insufficient documentation confirming adequate roof condition."
            )
    
    return decline_reasons

def show_decline_reasons_selection():
    """Show the decline reasons selection interface"""
    st.subheader("Select Declination Reason(s)")
    
    selected_reasons = []
    for key, value in DECLINE_REASONS.items():
        if st.checkbox(key):
            selected_reasons.append(value)
    
    if st.button("Generate Decline Email"):
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
        else:
            st.warning("Please select at least one decline reason")

def render_step1():
    """Render the first step of the submission process"""
    initialize_session_state()
    
    st.subheader("Property Information")
    
    # Form Fields
    with st.form("property_info_form"):
        effective_date = st.date_input(
            "Effective Date",
            value=st.session_state.effective_date,
            min_value=datetime.today().date()
        )
        
        association_name = st.text_input(
            "Name of Association",
            value=st.session_state.association_name
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            agency = st.selectbox(
                "Select Agency",
                options=AGENCIES,
                index=AGENCIES.index(st.session_state.agency) if st.session_state.agency in AGENCIES else 0
            )
            
            year_built = st.number_input(
                "Year Built",
                min_value=1900,
                max_value=datetime.today().year,
                value=st.session_state.year_built
            )
            
            stories = st.number_input(
                "Number of Stories",
                min_value=1,
                value=st.session_state.stories
            )
            
            construction_type = st.selectbox(
                "Construction Type",
                options=CONSTRUCTION_TYPES,
                index=CONSTRUCTION_TYPES.index(st.session_state.construction_type)
            )
        
        with col2:
            county = st.selectbox(
                "Select County",
                options=COUNTIES,
                index=COUNTIES.index(st.session_state.county) if st.session_state.county in COUNTIES else 0
            )
            
            roof_replacement = st.number_input(
                "Roof Replacement Year",
                min_value=1900,
                max_value=datetime.today().year,
                value=st.session_state.roof_replacement
            )
            
            tiv = st.number_input(
                "Total Insurable Value (TIV)",
                min_value=0.0,
                value=st.session_state.tiv,
                format="%.2f"
            )
            
            outdoor_property_tiv = st.number_input(
                "Outdoor Property TIV (if applicable)",
                min_value=0.0,
                value=st.session_state.outdoor_property_tiv,
                format="%.2f"
            )
        
        # Form buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        
        with col1:
            submit_button = st.form_submit_button("Continue")
        
        with col2:
            decline_button = st.form_submit_button("Decline")
        
        with col3:
            referral_button = st.form_submit_button("Send to Manager")

    # Handle form submission
    if submit_button or decline_button or referral_button:
        if not all([association_name, agency, county]):
            st.error("Please fill out all required fields.")
            return
        
        # Store values in session state
        st.session_state.update({
            'effective_date': effective_date,
            'association_name': association_name,
            'agency': agency,
            'county': county,
            'region': get_region_for_county(county),
            'year_built': year_built,
            'roof_replacement': roof_replacement,
            'stories': stories,
            'tiv': tiv,
            'construction_type': construction_type,
            'outdoor_property_tiv': outdoor_property_tiv,
            'needs_referral': tiv > 100_000_000 or (stories <= 3 and tiv > 60_000_000)
        })
        
        if referral_button:
            if st.session_state.needs_referral:
                # Get region from county
                region = get_region_for_county(county)

                email_data = generate_referral_email(
                    association_name=association_name,
                    agency=agency,
                    effective_date=effective_date,
                    stories=stories,
                    construction_type=construction_type,
                    year_built=year_built,
                    roof_replacement=roof_replacement,
                    tiv=tiv,
                    county=county,
                    region=region
                )
                st.info("### Submission Outcome: Referred to Manager")
                add_to_history(association_name, agency, "Referred to Manager")
                st.text("Email Subject:")
                st.text(email_data['subject'])
                st.text("Email Body:")
                st.text_area("Referral Email", email_data['body'], height=400)
            else:
                st.error("This submission does not qualify for referral.")
                return
                
        elif decline_button:
            st.session_state.showing_decline_reasons = True
            add_to_history(association_name, agency, "Declined")
            
        else:
            # Check for auto-decline conditions with updated validation
            decline_reasons = validate_submission(
                association_name=association_name,
                agency=agency,
                year_built=year_built,
                roof_replacement=roof_replacement,
                stories=stories,
                construction_type=construction_type,
                tiv=tiv,
                effective_date=effective_date
            )
            
            if decline_reasons:
                email_body = generate_declined_email(
                    association_name=association_name,
                    agency=agency,
                    year_built=year_built,
                    roof_replacement=roof_replacement,
                    stories=stories,
                    construction_type=construction_type,
                    tiv=tiv,
                    outdoor_property_tiv=outdoor_property_tiv,
                    effective_date=effective_date,
                    required_docs={},
                    selected_reasons=decline_reasons
                )
                st.error("### Submission Outcome: Declined")
                add_to_history(association_name, agency, "Declined")
                st.text_area("Generated Email", email_body, height=400)
            else:
                st.session_state.step = 2
                st.rerun()
    
    # Show decline reasons selection if needed
    if st.session_state.showing_decline_reasons:
        show_decline_reasons_selection()