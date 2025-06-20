"""
The referral email generated to send the manager for high TIV submissions
"""
from datetime import datetime
from typing import Optional

def generate_referral_email(
    association_name: str,
    agency: str,
    effective_date: datetime,
    stories: int,
    construction_type: str,
    year_built: int,
    roof_replacement: int,
    tiv: float,
    county: str,
    region: str
) -> dict:
    """
    Generate a referral email for high TIV submissions
    
    Returns:
        dict: Contains 'subject' and 'body' of the email
    """
    current_year = datetime.today().year
    
    # Calculate ages
    building_age = current_year - year_built
    roof_age = current_year - roof_replacement
    
    # Determine if roof is original
    roof_status = "Roof Original" if year_built == roof_replacement else f"Roof Replaced in {roof_replacement}"
    
    # Format TIV with commas and 2 decimal places
    formatted_tiv = "${:,.2f}".format(tiv)
    
    # Create email subject and body
    subject = f"Referral: {effective_date.strftime('%m/%d/%Y')} {association_name}"
    
    email_body = f"""Hi Karen,

We received this submission from {agency} and wanted to check if this is an account we should consider underwriting. Below is the submission summary:

{effective_date.strftime('%m/%d/%Y')} {association_name} located in the {region} region.
{stories} story {construction_type} buildings built in {year_built}. {roof_status}
TIV: {formatted_tiv}
Age of buildings: {building_age} years ({year_built})
Age of Roofs: {roof_age} years ({roof_replacement})
Address: 

Please let me know if you'd like to move forward with this account or if you prefer that I decline it.
Regards,"""

    return {
        'subject': subject,
        'body': email_body
    }