"""Utilities for handling document ordering and formatting"""

def sort_additional_docs(docs_list):
    """
    Sort additional documents according to predetermined priority order
    """
    # Define the order for documents
    doc_order = [
        "Building Updates",
        "Roof Condition Inspection",
        "Financials",
        "Reserve Study",
        "Board Meeting Minutes (3-5 years)",
        "Wind Mitigation",
        "Flood Policy",
        "Target Premium",
        "Renewal Premium",
        "Expiring Premium",
        "Association Documents",
        "Additional Loss History",
        "Producer",
        "Site Map",
        "Structural Inspection",
        "Engineer Inspection",
        "Prior Claims Experience"
    ]
    
    # Create a dictionary mapping doc names to their order
    order_dict = {name: index for index, name in enumerate(doc_order)}
    
    # Sort the documents based on the predefined order
    def get_sort_key(doc):
        # Extract the document name (everything before the colon)
        doc_name = doc.split(':')[0].strip()
        # Return its position in the order dict, or a large number if not found
        return order_dict.get(doc_name, len(doc_order))
    
    return sorted(docs_list, key=get_sort_key)

def format_premium_text(premiums_missing):
    """
    Format premium text in the desired format
    """
    if not premiums_missing:
        return None
    return "• Target, Renewal and Expiring Premiums"