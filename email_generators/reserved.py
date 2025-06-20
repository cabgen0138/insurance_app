from datetime import datetime, date, timedelta
from typing import Dict

def generate_reserved_email(
    association_name: str,
    agency: str,
    year_built: int,
    roof_replacement: int,
    stories: int,
    county: str,
    received_docs: Dict[str, bool],
    received_additional_docs: Dict[str, bool],
    effective_date: date
) -> str:
    """
    Generate a reserved status email with document requirements and deadlines.
    Building Updates and Roof Condition Inspection always listed first (if missing),
    then all other missing docs (including premiums) in the user's checkbox order.
    """
    if not isinstance(effective_date, datetime):
        effective_date = datetime.combine(effective_date, datetime.min.time())

    today = datetime.today()
    days_until = (effective_date - today).days

    # Determine deadline text
    if days_until >= 30:
        deadline = effective_date - timedelta(days=30)
        deadline_text = f"by **{deadline.strftime('%m/%d/%Y')}**"
    elif days_until >= 21:
        deadline_text = f"by **{(today + timedelta(days=21)).strftime('%m/%d/%Y')}**"
    elif days_until >= 14:
        deadline_text = f"by **{(today + timedelta(days=14)).strftime('%m/%d/%Y')}**"
    elif days_until >= 7:
        deadline_text = f"by **{(today + timedelta(days=7)).strftime('%m/%d/%Y')}**"
    else:
        deadline_text = "as soon as possible"

    # Order logic: always start with priority items (if present), then all others in original checkbox order
    priority_items = ["Building Updates", "Roof Condition Inspection"]
    missing_additional = [doc for doc, rec in received_additional_docs.items() if not rec]

    # Priority items in order, if missing
    priority_to_list = [item for item in priority_items if item in missing_additional]
    # All other missing items in checkbox order, excluding priority items
    rest_to_list = [doc for doc in missing_additional if doc not in priority_items]

    # Start email body
    email_body = (
        f"Hi,\n\n"
        f"Thank you for your submission of the above referenced account for {association_name}. "
        "This account has been reserved for your agency and is awaiting underwriting review."
    )

    # Preferred commission tier
    if year_built >= 1994 and roof_replacement >= 2010:
        email_body += (
            "\n\nBased on the risk characteristics, it appears that this account may qualify for our preferred commission tier. "
            "Eligibility for the preferred commission tier will be confirmed during the underwriting process."
        )

    # List missing additional docs
    if priority_to_list or rest_to_list:
        email_body += (
            "\n\nThe following additional documents are needed to proceed with the quote review process. "
            "Please send at your earliest convenience:"
        )
        # Priority first
        for doc in priority_to_list:
            email_body += f"\n• {doc}"
        # Then all others in UI order
        for doc in rest_to_list:
            email_body += f"\n• {doc}"

        # Add deadline and closing note
        if deadline_text == "as soon as possible":
            email_body += (
                "\n\nPlease supply the items listed above as soon as possible to retain your account reservation. "
                "If not received by the requested date, the reservation will be released. "
                "Contact us if you need additional time or assistance."
            )
        else:
            email_body += (
                f"\n\nPlease supply the items listed above {deadline_text} to retain your account reservation. "
                "If not received by the requested date, the reservation will be released. "
                "Contact us if you need additional time or assistance."
            )

    # Sign-off
    email_body += "\n\nKindest Regards,"
    return email_body
