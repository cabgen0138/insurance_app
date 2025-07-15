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
    for doc_name, description in BASE_ADDITIONAL_DOCS:
        if doc_name not in ["Engineer Inspection", "Prior Claims Experience"]:
            applicable_docs.append((doc_name, description))
    if has_supplemental:
        applicable_docs.extend([
            doc for doc in BASE_ADDITIONAL_DOCS
            if doc[0] in ["Engineer Inspection", "Prior Claims Experience"]
        ])
    assoc = st.session_state.association_name.lower()
    if not any(term in assoc for term in ['condo', 'condominium']):
        applicable_docs.append(("Association Documents", "Declarations and Bylaws"))
    if st.session_state.year_built <= 2017:
        applicable_docs.append(("Additional Loss History", "2017-2020 loss runs, if available"))
    if st.session_state.stories >= 3 and (current_year - st.session_state.year_built) >= 30:
        applicable_docs.append(("Structural Inspection", "Most recent structural or milestone inspection"))
    if year_built < 1980:
        applicable_docs.append(("Building Updates", "Provide documentation confirming the condition, type, and history of any updates to wiring and plumbing systems"))
    if (current_year - st.session_state.roof_replacement) >= 15:
        applicable_docs.append(("Roof Condition Inspection", "Provide a current roof condition inspection for all roofs that are 15+ years old"))
    return applicable_docs


def filter_loss_run_years(year_built: int) -> list:
    """Filter available loss run years based on year built"""
    current_year = datetime.today().year
    years = []
    start = max(2020, year_built)
    while start < current_year:
        years.append(f"Loss Runs {start}-{start+1}")
        start += 1
    return years


def show_decline_reasons_selection():
    """Show decline reasons for step 2, with optional bypass for high TIV"""
    st.subheader("Select Declination Reason(s)")
    selected = []
    for k, v in DECLINE_REASONS.items():
        if st.checkbox(k, key=f"step2_{k}"):
            selected.append(v)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Decline Email", key="step2_decline"):
            if selected:
                email = generate_declined_email(
                    association_name=st.session_state.association_name,
                    agency=st.session_state.agency,
                    year_built=st.session_state.year_built,
                    roof_replacement=st.session_state.roof_replacement,
                    stories=st.session_state.stories,
                    construction_type=st.session_state.construction_type,
                    tiv=st.session_state.tiv,
                    outdoor_property_tiv=0.0,
                    effective_date=st.session_state.effective_date,
                    required_docs={},
                    selected_reasons=selected
                )
                st.error("### Submission Outcome: Declined")
                st.text_area("Generated Email", email, height=400)
                st.session_state.showing_decline_reasons = False
    if (st.session_state.tiv > 100_000_000) or (st.session_state.stories <= 3 and st.session_state.tiv > 60_000_000):
        with col2:
            if st.button("Bypass Declination", key="step2_bypass"):
                st.session_state.showing_decline_reasons = False
                st.session_state.step = 2
                st.rerun()


def render_step2():
    """Render the second step of the submission process"""
    if st.session_state.showing_decline_reasons:
        show_decline_reasons_selection()
        return

    st.subheader("Submission Summary")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Effective Date:** {st.session_state.effective_date.strftime('%m/%d/%Y')}")
        st.write(f"**Association:** {st.session_state.association_name}")
        st.write(f"**Agency:** {st.session_state.agency}")
        st.write(f"**County:** {st.session_state.county}")
        st.write(f"**Region:** {st.session_state.region}")
    with c2:
        st.write(f"**Year Built:** {st.session_state.year_built}")
        st.write(f"**Roof Replacement:** {st.session_state.roof_replacement}")
        st.write(f"**Stories:** {st.session_state.stories}")
        st.write(f"**TIV:** ${st.session_state.tiv:,.2f}")

    with st.form("document_selection_form"):
        if not st.session_state.get('showing_additional_docs', False):
            st.subheader("Received Required Documents")
            basic = {doc: st.checkbox(doc) for doc in BASIC_REQUIRED_DOCS}
            years = filter_loss_run_years(st.session_state.year_built)
            loss = {}
            if years:
                colA, colB = st.columns(2)
                mid = len(years)//2
                with colA:
                    for y in years[:mid]: loss[y] = st.checkbox(y)
                with colB:
                    for y in years[mid:]: loss[y] = st.checkbox(y)
            btn1, btn2 = st.columns(2)
            with btn1:
                cont = st.form_submit_button("Continue")
            with btn2:
                back = st.form_submit_button("Back")
            if back:
                st.session_state.step = 1
                st.session_state.showing_additional_docs = False
                st.rerun()
            if cont:
                st.session_state.basic_docs = basic
                st.session_state.loss_run_docs = loss
                st.session_state.showing_additional_docs = True
                st.rerun()
        else:
            st.subheader("Select Received Documents")
            for d, r in st.session_state.basic_docs.items():
                if r: st.write(f"- {d}")
            for d, r in st.session_state.loss_run_docs.items():
                if r: st.write(f"- {d}")
            st.markdown("---")
            supp = st.session_state.basic_docs.get("Supplemental Application", False)
            add_docs = get_additional_docs(supp)
            rec_add = {}
            for name, desc in add_docs:
                label = f"{name}: {desc}" if desc else name
                rec_add[label] = st.checkbox(label)
            b_back, b_decline, b_submit, b_pipe = st.columns(4)
            with b_back:
                back2 = st.form_submit_button("Back")
            with b_decline:
                decline = st.form_submit_button("Decline")
            with b_submit:
                submit = st.form_submit_button("Submit")
            with b_pipe:
                pipe = st.form_submit_button("Copy Pipeline Data")
            if back2:
                st.session_state.showing_additional_docs = False
                st.rerun()
            elif decline:
                st.session_state.showing_decline_reasons = True
                return
            elif submit:
                received = {**st.session_state.basic_docs, **st.session_state.loss_run_docs}
                docsub = DocumentSubmission(required_docs=received, additional_docs=rec_add)
                if docsub.is_complete():
                    outcome = "Reserved"
                elif st.session_state.year_built >= 1980:
                    outcome = "Not Cleared - RFI"
                else:
                    outcome = "Not Cleared - OOA"
                if outcome == "Reserved":
                    body = generate_reserved_email(
                        association_name=st.session_state.association_name,
                        agency=st.session_state.agency,
                        year_built=st.session_state.year_built,
                        roof_replacement=st.session_state.roof_replacement,
                        stories=st.session_state.stories,
                        county=st.session_state.county,
                        received_docs=received,
                        received_additional_docs=rec_add,
                        effective_date=st.session_state.effective_date
                    )
                    st.success("### Submission Outcome: Reserved")
                    add_to_history(st.session_state.association_name, st.session_state.agency, "Reserved")
                else:
                    body = generate_not_cleared_email(
                        association_name=st.session_state.association_name,
                        agency=st.session_state.agency,
                        year_built=st.session_state.year_built,
                        roof_replacement=st.session_state.roof_replacement,
                        stories=st.session_state.stories,
                        county=st.session_state.county,
                        received_docs=received,
                        received_additional_docs=rec_add
                    )
                    st.warning(f"### Submission Outcome: {outcome}")
                    add_to_history(st.session_state.association_name, st.session_state.agency, outcome)
                st.text_area("Generated Email", body, height=400)
                data = get_pipeline_data(
                    effective_date=st.session_state.effective_date,
                    association_name=st.session_state.association_name,
                    agency=st.session_state.agency,
                    region=st.session_state.region,
                    stories=st.session_state.stories,
                    year_built=st.session_state.year_built,
                    tiv=st.session_state.tiv,
                    submission_status=outcome
                )
                st.text_input("Pipeline Data (Click to select, then Ctrl+C to copy)", value=data, key="pipeline_copy_field")
