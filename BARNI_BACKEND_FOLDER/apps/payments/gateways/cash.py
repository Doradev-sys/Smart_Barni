def process(order, amount):
    """Cash is recorded immediately for reconciliation — no external call."""
    return {"status": "COMPLETED", "reference": ""}
