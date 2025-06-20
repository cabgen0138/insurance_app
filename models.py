""" Data models and validation logic for the insurance app """
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Dict, List
from config import (
    MIN_TIV, MAX_TIV, MAX_GARDEN_STYLE_TIV, 
    MAX_FRAME_STORIES, MAX_EFFECTIVE_DATE_DAYS
)

@dataclass
class PropertySubmission:
    association_name: str
    agency: str
    county: str
    effective_date: date
    year_built: int
    roof_replacement: int
    stories: int
    tiv: float
    construction_type: str

    def validate(self) -> List[str]:
        """
        Validates the submission and returns a list of decline reasons if any
        Returns empty list if submission is valid
        """
        decline_reasons = []
        today = datetime.today()
        
        # Basic validation checks
        if self.agency == "Unknown":
            decline_reasons.append("Agency Not Appointed")
        
        if (self.construction_type == "Frame" and 
            self.stories > MAX_FRAME_STORIES):
            decline_reasons.append(
                f"Frame > {MAX_FRAME_STORIES} stories: The subject property includes "
                f"predominantly frame building(s) > {MAX_FRAME_STORIES} stories."
            )
        
        if ((self.effective_date - today.date()).days > 
            MAX_EFFECTIVE_DATE_DAYS):
            decline_reasons.append(
                "Effective Date: Requested effective date is > 120 days past "
                "the submission date; account cannot be reserved at this time."
            )
        
        # TIV-based checks
        building_age = today.year - self.year_built
        roof_age = today.year - self.roof_replacement
        
        if self.tiv < MIN_TIV:
            decline_reasons.append(
                f"TIV < ${MIN_TIV/1_000_000}M: TIV is less than ${MIN_TIV/1_000_000:,}M"
            )
        elif self.tiv > MAX_TIV:
            decline_reasons.append(
                f"TIV > ${MAX_TIV/1_000_000}M: Per premises TIV exceeds ${MAX_TIV/1_000_000}M"
            )
        elif (self.stories <= 3 and 
              self.tiv > MAX_GARDEN_STYLE_TIV):
            decline_reasons.append(
                f"Garden Style TIV > ${MAX_GARDEN_STYLE_TIV/1_000_000}M: Per premises TIV "
                f"exceeds ${MAX_GARDEN_STYLE_TIV/1_000_000}M. We are generally looking for "
                f"${MIN_TIV/1_000_000}M-${MAX_GARDEN_STYLE_TIV/1_000_000}M TIVs for garden style risks."
            )
        
        # Age-based checks
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

@dataclass
class DocumentSubmission:
    required_docs: Dict[str, bool]
    additional_docs: Dict[str, bool]

    def is_complete(self) -> bool:
        """Check if all required documents are submitted"""
        return all(self.required_docs.values())

    def get_missing_docs(self) -> List[str]:
        """Get list of missing required documents"""
        return [doc for doc, received in self.required_docs.items() 
                if not received]