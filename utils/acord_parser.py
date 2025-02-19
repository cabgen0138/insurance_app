"""ACORD PDF parser utility."""
import pdfplumber
from typing import Dict, Any, Optional
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AcordParser:
    """Parser for ACORD 125/140 forms."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extract_fields(self) -> Dict[str, Any]:
        """
        Extracts relevant fields from ACORD PDF.
        Returns a dictionary of field names and values.
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                data = {}
                
                # Process each page
                for page in pdf.pages:
                    text = page.extract_text()
                    
                    # Extract fields using regex patterns
                    data.update(self._extract_named_insured(text))
                    data.update(self._extract_effective_date(text))
                    data.update(self._extract_construction(text))
                    data.update(self._extract_year_built(text))
                    data.update(self._extract_stories(text))
                    data.update(self._extract_tiv(text))
                    
                return data
                
        except Exception as e:
            logger.error(f"Error parsing ACORD PDF: {str(e)}")
            raise ValueError(f"Error parsing ACORD PDF: {str(e)}")

    def _extract_named_insured(self, text: str) -> Dict[str, str]:
        """Extracts the named insured (association name)."""
        match = re.search(r"NAMED INSURED\s*(.+?)(?=\n|\s{2,})", text)
        return {"association_name": match.group(1).strip()} if match else {}

    def _extract_effective_date(self, text: str) -> Dict[str, datetime]:
        """Extracts the effective date."""
        match = re.search(r"EFFECTIVE DATE\s*(\d{2}[-/]\d{2}[-/]\d{4})", text)
        if match:
            date_str = match.group(1)
            try:
                # Handle different date separators
                date_str = date_str.replace('-', '/')
                return {"effective_date": datetime.strptime(date_str, '%m/%d/%Y').date()}
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
        return {}

    def _extract_construction(self, text: str) -> Dict[str, str]:
        """Extracts the construction type."""
        match = re.search(r"CONSTRUCTION(?:\s+TYPE)?\s*[:;]?\s*(\w+)", text, re.I)
        return {"construction_type": match.group(1).upper()} if match else {}

    def _extract_year_built(self, text: str) -> Dict[str, int]:
        """Extracts the year built."""
        match = re.search(r"YEAR\s+BUILT\s*[:;]?\s*(\d{4})", text, re.I)
        return {"year_built": int(match.group(1))} if match else {}

    def _extract_stories(self, text: str) -> Dict[str, int]:
        """Extracts the number of stories."""
        match = re.search(r"(?:NO\.|NUMBER\s+OF)\s+STORIES\s*[:;]?\s*(\d+)", text, re.I)
        return {"stories": int(match.group(1))} if match else {}

    def _extract_tiv(self, text: str) -> Dict[str, float]:
        """Extracts the Total Insurable Value."""
        match = re.search(r"TOTAL\s+(?:INSURABLE\s+)?VALUE\s*[:;]?\s*\$?\s*([\d,]+)", text, re.I)
        if match:
            try:
                value = float(match.group(1).replace(',', ''))
                return {"tiv": value}
            except ValueError:
                logger.warning(f"Could not parse TIV value: {match.group(1)}")
        return {}