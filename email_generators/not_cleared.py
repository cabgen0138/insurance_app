from datetime import datetime
from typing import Dict, List
from utils.premium_utils import get_missing_premiums_text

def consolidate_years(missing_loss_runs: List[str]) -> str:
    """
    Convert missing loss runs years into consolidated ranges.
    E.g., ["Loss Runs 2021-2022", "Loss Runs 2022-2023", "Loss Runs 2023-2024"] -> "2021-2024"
    """
    if not missing_loss_runs:
        return ""

    # Create pairs of start and end years
    year_pairs = []
    for loss_run in missing_loss_runs:
        year_range = loss_run.replace("Loss Runs ", "")
        start, end = map(int, year_range.split("-"))
        year_pairs.append((start, end))
    
    # Sort by start year
    year_pairs.sort()
    
    # Find consecutive ranges
    ranges = []
    current_start, current_end = year_pairs[0]
    
    for start, end in year_pairs[1:]:
        if start == current_end:  # Years are consecutive
            current_end = end
        else:  # Gap in years, start new range
            ranges.append(f"{current_start}-{current_end}")
            current_start = start
            current_end = end
    
    # Add the last range
    ranges.append(f"{current_start}-{current_end}")
    
    # Join ranges with " and "
    return " and ".join(ranges)

def generate_not_cleared_email(
    association_name: str,
    agency: str,
    year_built: int,
    roof_replacement: int,
    stories: int,
    county: str,
    received_docs: Dict[str, bool],
    received_additional_docs: Dict[str, bool]
) -> str:
    """
    Generate a not cleared email listing missing documents and requirements
    """
    email_body = f"""Hi,

Thank you for your submission of the above referenced account for {association_name}."""

    # Check for preferred commission tier eligibility
    if year_built >= 1994 and roof_replacement >= 2010:
        email_body += """

Based on the risk characteristics, it appears that this account may qualify for our preferred commission tier. 
Eligibility for the preferred commission tier will be confirmed during the underwriting process."""

    # Get missing documents
    missing_initial_docs = [doc for doc, received in received_docs.items() 
                          if not received]

    # Separate loss runs from other missing documents
    missing_loss_runs = [doc for doc in missing_initial_docs if "Loss Runs" in doc]
    other_missing_docs = [doc for doc in missing_initial_docs if "Loss Runs" not in doc]

    # If there are any missing documents (including loss runs)
    if missing_initial_docs:
        email_body += """

The following additional documents are needed to reserve the account. Please send at your earliest convenience."""
        
        # First list non-loss run documents
        for doc in other_missing_docs:
            email_body += f"\n• {doc}"
        
        # Then add formatted loss runs if any are missing
        if missing_loss_runs:
            year_ranges = consolidate_years(missing_loss_runs)
            if year_ranges:
                email_body += f"\n• Loss Runs: Currently valued {year_ranges} loss runs (outdated loss runs or a SONL can be accepted in lieu of currently valued loss runs for reservation purposes)"

    # Handle additional documents
    missing_additional_docs = [doc for doc, received in received_additional_docs.items() 
                             if not received and not any(premium in doc for premium in 
                             ["Target Premium", "Renewal Premium", "Expiring Premium"])]
    
    # Get missing premiums text
    missing_premiums = get_missing_premiums_text(received_additional_docs)
    
    if missing_additional_docs or missing_premiums:
        email_body += """

If reserved, we will request the additional items outlined below. Please be aware that starred items are required to confirm eligibility. 
Please let us know at your earliest opportunity if these items are not available."""
        
        # Add non-premium missing documents
        for doc in missing_additional_docs:
            email_body += f"\n• {doc}"
            
        # Add missing premiums if any
        if missing_premiums:
            email_body += f"\n{missing_premiums}"

    email_body += """

We appreciate your partnership!

Kindest Regards,"""

    return email_body