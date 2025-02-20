def get_missing_premiums_text(received_additional_docs: dict) -> str:
    """
    Generate text for missing premiums based on which ones were received
    """
    target_received = any("Target Premium" in doc and received for doc, received in received_additional_docs.items())
    renewal_received = any("Renewal Premium" in doc and received for doc, received in received_additional_docs.items())
    expiring_received = any("Expiring Premium" in doc and received for doc, received in received_additional_docs.items())
    
    missing_premiums = []
    if not target_received:
        missing_premiums.append("Target")
    if not renewal_received:
        missing_premiums.append("Renewal")
    if not expiring_received:
        missing_premiums.append("Expiring")
    
    if not missing_premiums:
        return None  # All premiums received
        
    if len(missing_premiums) == 1:
        return f"• {missing_premiums[0]} Premium"
    elif len(missing_premiums) == 2:
        return f"• {missing_premiums[0]} and {missing_premiums[1]} Premiums"
    else:
        return f"• Target, Renewal and Expiring Premiums"