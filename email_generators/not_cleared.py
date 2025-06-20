from datetime import datetime
from typing import Dict, List

def consolidate_years(missing_loss_runs: List[str]) -> str:
    """
    Convert missing loss runs years into consolidated ranges.
    E.g. ["Loss Runs 2021-2022", "Loss Runs 2022-2023", "Loss Runs 2023-2024"] -> "2021-2024"
    """
    if not missing_loss_runs:
        return ""

    # Parse year pairs
    year_pairs = []
    for loss_run in missing_loss_runs:
        yrs = loss_run.replace("Loss Runs ", "").split("-")
        start, end = int(yrs[0]), int(yrs[1])
        year_pairs.append((start, end))
    year_pairs.sort()

    # Consolidate consecutive ranges
    ranges: List[str] = []
    current_start, current_end = year_pairs[0]
    for start, end in year_pairs[1:]:
        if start == current_end:
            current_end = end
        else:
            ranges.append(f"{current_start}-{current_end}")
            current_start, current_end = start, end
    ranges.append(f"{current_start}-{current_end}")

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
    Generate a not cleared email listing missing documents and requirements,
    preserving checkbox order and always putting Building Updates/Roof Inspection first if missing.
    """
    # Header
    email_body = (
        f"Hi,\n\n"
        f"Thank you for your submission of the above referenced account for {association_name}."
    )

    # Preferred commission tier note
    if year_built >= 1994 and roof_replacement >= 2010:
        email_body += (
            "\n\nBased on the risk characteristics, it appears that this account may qualify "
            "for our preferred commission tier. Eligibility will be confirmed during underwriting."
        )

    # Identify missing initial documents
    missing_initial = [doc for doc, received in received_docs.items() if not received]
    missing_loss_runs = [d for d in missing_initial if "Loss Runs" in d]
    other_missing = [d for d in missing_initial if "Loss Runs" not in d]

    if missing_initial:
        email_body += (
            "\n\nThe following documents are needed to reserve the account. "
            "Please send at your earliest convenience:"
        )
        # List non-loss runs
        for doc in other_missing:
            email_body += f"\n• {doc}"
        # Consolidated loss runs
        if missing_loss_runs:
            ranges = consolidate_years(missing_loss_runs)
            if ranges:
                email_body += (
                    f"\n• Loss Runs: Valued {ranges} loss runs "
                    "(outdated loss runs or SONL accepted in lieu for reservation)"
                )

    # Identify missing additional documents and preserve checkbox/UI order
    priority_items = ["Building Updates", "Roof Condition Inspection"]
    missing_additional = [doc for doc, received in received_additional_docs.items() if not received]
    priority_to_list = [item for item in priority_items if item in missing_additional]
    rest_to_list = [doc for doc in missing_additional if doc not in priority_items]

    if priority_to_list or rest_to_list:
        email_body += (
            "\n\nIf reserved, we will request the additional items below. "
            "Please note required items and advise if unavailable:"
        )
        # Priority first
        for doc in priority_to_list:
            email_body += f"\n• {doc}"
        # All others in UI order (including premiums)
        for doc in rest_to_list:
            email_body += f"\n• {doc}"

    # Closing
    email_body += (
        "\n\nWe appreciate your partnership!\n\n"
        "Kindest Regards,"
    )
    return email_body