from datetime import datetime, date, timedelta
from typing import Dict
from utils.premium_utils import get_missing_premiums_text
from utils.document_utils import sort_additional_docs, format_premium_text

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
    Generate a reserved status email with document requirements and deadlines
    """
    from utils.document_utils import sort_additional_docs, format_premium_text
    
    today = datetime.today()
    
    if not isinstance(effective_date, datetime):
        effective_date = datetime.combine(effective_date, datetime.min.time())
    
    time_until_effective = effective_date - today
    days_until_effective = time_until_effective.days
    
    # Determine deadline based on time until effective date
    if days_until_effective >= 30:
        deadline = effective_date - timedelta(days=30)
        deadline_text = f"by **{deadline.strftime('%m/%d/%Y')}**"
    elif days_until_effective >= 21:
        deadline_text = f"by **{(today + timedelta(days=21)).strftime('%m/%d/%Y')}**"
    elif days_until_effective >= 14:
        deadline_text = f"by **{(today + timedelta(days=14)).strftime('%m/%d/%Y')}**"
    elif days_until_effective >= 7:
        deadline_text = f"by **{(today + timedelta(days=7)).strftime('%m/%d/%Y')}**"
    else:
        deadline_text = "as soon as possible"

    # Get list of missing additional documents (excluding premiums)
    missing_additional_docs = [doc for doc, received in received_additional_docs.items() 
                             if not received and not any(premium in doc for premium in 
                             ["Target Premium", "Renewal Premium", "Expiring Premium"])]

    # Check for missing premiums
    premium_docs = ["Target Premium", "Renewal Premium", "Expiring Premium"]
    premiums_missing = any(
        not received_additional_docs.get(doc, False) 
        for doc in received_additional_docs 
        if any(premium in doc for premium in premium_docs)
    )

    email_body = f"""Hi,

Thank you for your submission of the above referenced account for {association_name}. This account has been reserved for your agency and is awaiting underwriting review."""

    # Add preferred commission tier message if eligible
    if year_built >= 1994 and roof_replacement >= 2010:
        email_body += """

Based on the risk characteristics, it appears that this account may qualify for our preferred commission tier. 
Eligibility for the preferred commission tier will be confirmed during the underwriting process."""

    # Add missing document requirements if any
    if missing_additional_docs or premiums_missing:
        email_body += """

The following additional documents are needed to proceed with the quote review process. The starred items are required to quote. Please send at your earliest convenience."""
        
        # Get sorted documents
        sorted_docs = sort_additional_docs(missing_additional_docs)
        
        # Process documents in order with premium insertion
        for doc in sorted_docs:
            doc_name = doc.split(':')[0].strip()
            
            # Add the document
            email_body += f"\n• {doc}"
            
            # Add premiums after Flood Policy
            if premiums_missing and doc_name == "Flood Policy":
                email_body += "\n• Target, Renewal and Expiring Premiums"

        if deadline_text == "as soon as possible":
            email_body += f"""

Please supply the items listed above as soon as possible to retain your account reservation. 

If not received by the requested date, please be aware the reservation will be released. Do not hesitate to contact us if you encounter any challenges or need additional time to obtain the requested documents."""
        else:
            email_body += f"""

Please supply the items listed above {deadline_text} to retain your account reservation. 

If not received by the requested date, please be aware the reservation will be released. Do not hesitate to contact us if you encounter any challenges or need additional time to obtain the requested documents."""

    email_body += """

Kindest Regards,"""

    return email_body