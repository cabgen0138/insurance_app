"""
Generator for declined submission emails
"""
from datetime import datetime, date
from typing import Dict, List, Optional

def generate_declined_email(
    association_name: str,
    agency: str,
    year_built: int,
    roof_replacement: int,
    stories: int,
    construction_type: str,
    tiv: float,
    effective_date: date,
    required_docs: Dict[str, bool],
    selected_reasons: Optional[List[str]] = None
) -> str:
    """
    Generate a decline email based on provided reasons or auto-decline conditions.
    """
    today = datetime.today()
    decline_reasons = []

    if selected_reasons:
        # Only include manually selected reasons
        decline_reasons.extend(selected_reasons)

    else:
        # Auto-decline logic
        if agency == "Unknown":
            decline_reasons.append("Agency Not Appointed")

        if construction_type == "Frame" and stories > 5:
            decline_reasons.append(
                "Frame > 5 stories: The subject property includes predominantly "
                "frame building(s) > 5 stories."
            )

        if (effective_date - today.date()).days > 120:
            decline_reasons.append(
                "Effective Date: Requested effective date is > 120 days past "
                "the submission date; account cannot be reserved at this time."
            )

        # TIV-based checks
        building_age = today.year - year_built
        roof_age = today.year - roof_replacement

        if tiv < 5_000_000:
            decline_reasons.append("TIV < $5M: TIV is less than $5,000,000")
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

        if tiv > 100_000_000:
            decline_reasons.append("TIV > $100M: Per premises TIV exceeds $100M")
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

        if stories <= 3 and tiv > 60_000_000:
            decline_reasons.append(
                "Garden Style TIV > $60M: Per premises TIV exceeds $60M. We are generally "
                "looking for $5M-$60M TIVs for garden style risks."
            )
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

    # Generate the email body
    email_body = f"""Hello,

Thank you for your submission of the above referenced account. Upon review, it was found that the account does not meet our current selection criteria. The primary reason(s) for declination is outlined below.

"""

    # Add decline reasons
    for reason in decline_reasons:
        email_body += f"{reason}\n"

    email_body += """
Should you have any questions regarding the reason(s) for declination, please do not hesitate to contact us.

We thank you for considering us as a market for your account.  

Kindest Regards,"""

    return email_body
