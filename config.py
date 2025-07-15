from datetime import datetime, date

# Agency and location constants
AGENCIES = [
    "Acentria – Destin", "Acentria - Panama City", "Acentria - Port St Lucie", "Acrisure - Fletcher & Co",
    "Acrisure - Gambrell & Sturges", "Acrisure – Gulfshore", "AJG – Harden", "Alliant", "AP – IRMS",
    "AP - Lake Mary", "AP - Mack Mack & Waltz", "AP – Ranew", "Briercheck", "Brown & Brown - Daytona Beach",
    "Brown & Brown – Jacksonville", "Brown & Brown – Sarasota", "Brown & Brown – West Palm", "Chapman Insurance",
    "Cothrom", "Darr Schackow", "Fisher Brown", "Franklin Hamilton", "Herbie Wiles",
    "Higginbotham - McMahon Hadder", "IJR - Advanced Insurance", "Marsh & McLennan – Bouchard",
    "McGriff - St Pete", "Plastridge", "RTI", "Sihle - Altamonte Springs", "Thompson Baker", "USI – Tampa", "Wellhouse", "Unknown"
]

COUNTIES = [
    "Alachua", "Baker", "Bay", "Bradford", "Brevard", "Broward", "Calhoun", "Charlotte", "Citrus", "Clay",
    "Collier", "Columbia", "Desoto", "Dixie", "Duval", "Escambia", "Flagler", "Franklin", "Gadsden", 
    "Gilchrist", "Glades", "Gulf", "Hamilton", "Hardee", "Hendry", "Hernando", "Highlands", "Hillsborough",
    "Holmes", "Indian River", "Jackson", "Jefferson", "Lafayette", "Lake", "Lee", "Leon", "Levy", "Liberty",
    "Madison", "Manatee", "Marion", "Martin", "Miami-Dade", "Monroe", "Nassau", "Okaloosa", "Okeechobee",
    "Orange", "Osceola", "Palm Beach", "Pasco", "Pinellas", "Polk", "Putnam", "Santa Rosa", "Sarasota",
    "Seminole", "St. Johns", "St. Lucie", "Sumter", "Suwannee", "Taylor", "Union", "Volusia", "Wakulla",
    "Walton", "Washington"
]

CONSTRUCTION_TYPES = ["Frame", "JM", "NC", "MNC", "MFR", "FR"]

# Region mapping
REGION_COUNTY_MAPPING = {
    "Big Bend": ["Alachua", "Bradford", "Citrus", "Columbia", "Dixie", "Gilchrist", "Hamilton", 
                 "Lafayette", "Levy", "Marion", "Suwannee", "Taylor", "Union"],
    "Northeast": ["Baker", "Clay", "Duval", "Flagler", "Nassau", "Putnam", "St. Johns"],
    "Panhandle": ["Bay", "Calhoun", "Escambia", "Franklin", "Gadsden", "Gulf", "Holmes", "Jackson", 
                  "Jefferson", "Leon", "Liberty", "Madison", "Okaloosa", "Santa Rosa", "Wakulla", 
                  "Walton", "Washington"],
    "Space Coast": ["Brevard", "Indian River", "Martin", "St. Lucie", "Volusia"],
    "Tri-County": ["Broward", "Miami-Dade", "Monroe", "Palm Beach"],
    "Southwest": ["Charlotte", "Collier", "Desoto", "Glades", "Hendry", "Lee"],
    "Tampa/St Pete": ["Hernando", "Hillsborough", "Manatee", "Pasco", "Pinellas", "Sarasota"],
    "Central": ["Hardee", "Highlands", "Lake", "Okeechobee", "Orange", "Osceola", "Polk", 
                "Seminole", "Sumter"]
}

# Basic required documents
BASIC_REQUIRED_DOCS = ["Acord 125/140", "SOV", "Supplemental Application", "Appraisal"]

# Base additional documents
BASE_ADDITIONAL_DOCS = [
    ("Financials", ""),
    ("Reserve Study", ""),
    ("Board Meeting Minutes (3-5 years)", ""),
    ("Wind Mitigation", ""),
    ("Flood Policy", ""),
    ("Target Premium", ""),
    ("Renewal Premium", ""),
    ("Expiring Premium", ""),
    ("Engineer Inspection", "Provide any engineering reports on defects or investigations referenced in the submission"),
    ("Producer", "Confirm the name of the client-facing producer"),
    ("Site Map", "Labeled map identifying the location of all buildings"),
    ("Prior Claims Experience", "Our objective is to build a book of business with clients who are inclined to file a claim with us directly before engaging third party assistance. Please supply any additional information you feel pertinent to our evaluation of the applicant's prior claim experience.")
]

# Validation constants
MIN_TIV = 5_000_000
MAX_TIV = 100_000_000
MAX_GARDEN_STYLE_TIV = 60_000_000
MAX_FRAME_STORIES = 5
MAX_EFFECTIVE_DATE_DAYS = 120

# Decline reasons mapping
DECLINE_REASONS = {
    "Regional Capacity": "Regional Capacity: The account is not being pursued due to current regional capacity limitations.",
    "Building Age": "Building Age/Updates: Building age(s) exceeds 30 years and there is insufficient documentation confirming adequate building updates.",
    "Roof Age": "Roof Age/Updates: Roof age(s) exceeds 15 years and there is insufficient documentation confirming adequate roof condition.",
    "Building Valuation": "Building Valuation: Building valuation is < $120/sf and/or is not aligned with the standard valuation range for like kind and quality construction.",
    "No Opening Protection": "No Opening Protection on Coast: The property lacks opening protection and is located on the coast.",
    "Flood Insurance": "Flood Insurance: The subject property is within 3 miles of the coast and no documentation was received confirming flood insurance is in place.",
    "Loss History": "Loss History: The applicant's loss history does not align with program guidelines.",
    "Open Claim": "Open Claim: There is a current open claim that does not align with program guidelines.",
    "No Prior Insurance": "No prior insurance: Risks with no prior insurance do not meet program eligibility guidelines.",
    "Midterm Submission": "Midterm Submission: Midterm submissions do not meet program eligibility guidelines.",
    "PC 9 or 10": "PC 9 or 10: The subject property is in a protection class 9 or 10 region.",
    "Existing Damage": "Existing Damage: There is existing unrepaired damage that does not align with program guidelines.",
    "Limited Access": "Limited means of ingress/egress: Communities in areas with less than 2 means of ingress/egress do not align with underwriting appetite.",
    "Occupancy": "Occupancy: Properties with less than 50% residential occupancy do not meet program eligibility guidelines.",
    "Additional Declination Reasons": "Additional Declination Reasons: Please be aware there may be additional factors influencing the reason for decline that were not identified in the initial review. Resubmission of this account with additional information addressing the above referenced items may not necessarily result in the account being reopened and reserved."
}

# Functions
def generate_loss_run_years():
    """Generate list of required loss run years"""
    current_year = datetime.today().year
    years = []
    # Start from 5 years ago
    start_year = current_year - 5
    while start_year < current_year:
        years.append(f"Loss Runs {start_year}-{start_year + 1}")
        start_year += 1
    return years

def get_region_for_county(county: str) -> str:
    """Get the region name for a given county"""
    for region, counties in REGION_COUNTY_MAPPING.items():
        if county in counties:
            return region
    return "Unknown Region"

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

# Combine basic docs with loss run years
REQUIRED_DOCS = BASIC_REQUIRED_DOCS + generate_loss_run_years()