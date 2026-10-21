def calculate_emi(principal: float, rate: float, tenure: int) -> dict:
    """Reducing-balance EMI. `rate` is annual percent, `tenure` is months."""
    if principal <= 0 or tenure <= 0 or rate < 0:
        raise ValueError("principal and tenure must be positive, rate non-negative")
    r = rate / 12 / 100
    emi = principal / tenure if r == 0 else principal * r * (1 + r) ** tenure / ((1 + r) ** tenure - 1)
    total = emi * tenure
    return {
        "principal": round(principal),
        "rate": rate,
        "tenure": tenure,
        "emi": round(emi),
        "total_payable": round(total),
        "total_interest": round(total - principal),
    }
