"""Tool registry: implementations plus OpenAI-style function schemas (used in stage prompts)."""
from tools.crm import crm_lookup
from tools.emi import calculate_emi
from tools.scheduler import book_callback

TOOLS = {"calculate_emi": calculate_emi, "crm_lookup": crm_lookup, "book_callback": book_callback}

TOOL_SCHEMAS = {
    "calculate_emi": {
        "name": "calculate_emi",
        "description": "Compute the monthly EMI for a loan.",
        "parameters": {"type": "object", "required": ["principal", "rate", "tenure"], "properties": {
            "principal": {"type": "number", "description": "Loan amount in INR"},
            "rate": {"type": "number", "description": "Annual interest rate in percent"},
            "tenure": {"type": "integer", "description": "Tenure in months"},
        }},
    },
    "crm_lookup": {
        "name": "crm_lookup",
        "description": "Fetch the customer's record and pre-approved offer.",
        "parameters": {"type": "object", "required": ["phone"], "properties": {"phone": {"type": "string"}}},
    },
    "book_callback": {
        "name": "book_callback",
        "description": "Book a callback. Must be in the future and between 09:00 and 21:00 IST.",
        "parameters": {"type": "object", "required": ["time"], "properties": {
            "time": {"type": "string", "description": "ISO 8601 datetime with +05:30 offset"},
        }},
    },
}
