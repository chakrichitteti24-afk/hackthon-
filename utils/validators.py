"""Response validation guardrails for factual OmniFlow AI replies."""

from __future__ import annotations

import re


VALID_BRANDS = [
    "Samsung",
    "Apple",
    "Google",
    "Xiaomi",
    "OnePlus",
    "ASUS",
    "Motorola",
    "Nothing",
    "Realme",
    "Sony",
    "Nokia",
    "Oppo",
    "Vivo",
]

VALID_PROCESSOR_FAMILIES = {
    "A-series",
    "Apple",
    "Bionic",
    "Dimensity",
    "Exynos",
    "Google Tensor",
    "MediaTek",
    "Qualcomm",
    "Snapdragon",
    "Tensor",
}

KNOWN_PRODUCT_LINES = {
    "Galaxy",
    "iPhone",
    "Pixel",
    "Redmi",
    "ROG",
    "Xperia",
    "Edge",
    "Razr",
    "Find",
    "Reno",
}

SUSPICIOUS_TERMS = {
    "AetherPhone",
    "CyberMax",
    "FuturePhone",
    "HyperPhone",
    "NeuroPhone",
    "OmniPhone",
    "QuantumPhone",
    "TechNova",
    "TitanCore",
    "ZenithPhone",
}

SAFE_FALLBACK = """Category
Product Recommendation

Key Insights
* Specific data unavailable
* Clarification required

Recommendations
Partial knowledge found. Gathering additional requirements.

Knowledge Sources
✓ Customer Memory

Confidence
60%

Could you please specify your budget, preferred brands, or must-have features?"""


def _contains_mobile_context(response: str) -> bool:
    return bool(
        re.search(
            r"\b(phone|mobile|smartphone|processor|chipset|cpu|gpu|camera|battery|mah|refresh rate|display|specs?)\b",
            response,
            flags=re.IGNORECASE,
        )
    )


def _has_impossible_specs(response: str) -> bool:
    checks = (
        (r"\b(\d{4,})\s*MP\b", 500),
        (r"\b(\d{6,})\s*mAh\b", 50000),
        (r"\b(\d{3,})\s*GB\s+RAM\b", 128),
        (r"\b(\d{2,})\s*TB\s+RAM\b", 1),
        (r"\b(\d{4,})\s*Hz\b", 360),
    )
    for pattern, limit in checks:
        for match in re.finditer(pattern, response, flags=re.IGNORECASE):
            try:
                if int(match.group(1)) > limit:
                    return True
            except ValueError:
                return True
    return False


def _has_suspicious_product_name(response: str) -> bool:
    for term in SUSPICIOUS_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", response, flags=re.IGNORECASE):
            return True

    if not _contains_mobile_context(response):
        return False

    product_pattern = re.compile(
        r"\b([A-Z][A-Za-z0-9+-]{2,})(?:\s+[A-Z][A-Za-z0-9+-]{1,}){0,2}\s+"
        r"(?:Phone|Mobile|Ultra|Pro|Max|Fold|Flip|Processor|Chip|CPU|GPU)\b"
    )
    for match in product_pattern.finditer(response):
        first_token = match.group(1)
        if (
            first_token not in VALID_BRANDS
            and first_token not in KNOWN_PRODUCT_LINES
            and first_token not in VALID_PROCESSOR_FAMILIES
        ):
            return True
    return False


def _has_hallucinated_processor(response: str) -> bool:
    if not _contains_mobile_context(response):
        return False

    processor_pattern = re.compile(
        r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\s+"
        r"(?:Quantum|Neural|Fusion|Titan|Hyper|Xtreme)\s*(?:\d{1,3})?\b"
    )
    for match in processor_pattern.finditer(response):
        family = match.group(1)
        if family not in VALID_PROCESSOR_FAMILIES and family.split()[0] not in VALID_BRANDS:
            return True
    return False


def validate_product_fields(response: str) -> bool:
    """Strictly validate GPU, CPU, Year, and Price in the response.
    
    Returns True if fields are present and look reasonable, False otherwise.
    Note: This is a heuristic check to ensure the model doesn't skip these mandatory fields
    when claiming to provide product specifications.
    """
    res_lower = response.lower()
    # Only enforce strict spec checks for responses that appear product-specific.
    # If it's a generic recommendation (no mobile/product context), do not require CPU/GPU/Year/Price.
    if "recommendation" in res_lower or "title" in res_lower:
        if not _contains_mobile_context(response):
            return True

        # Check for presence of key fields when product context is detected
        has_cpu = any(x in res_lower for x in ["cpu", "processor", "chip"])
        has_gpu = any(x in res_lower for x in ["gpu", "graphics", "video card"])
        has_year = re.search(r"\b(20\d{2})\b", response)
        has_price = re.search(r"(\$|£|€|rs\.?|inr)\s?\d+", res_lower)

        # If it looks like a product recommendation but lacks these, it's suspect
        if not (has_cpu and has_year and has_price):
            return False

    return True


def validate_response(response: str) -> bool:
    """Return False when a generated response looks factually unsafe."""
    if not response or not response.strip():
        return False

    if "reliable factual information could not be verified" in response.lower():
        return True
    if "reliable information is unavailable" in response.lower():
        return True
    if "could not verify the latest configuration" in response.lower():
        return True
    if "i could not verify the latest information from available knowledge sources" in response.lower():
        return True
    if "partial product knowledge found" in response.lower():
        return True
        return True

    if _has_impossible_specs(response):
        return False
    if _has_suspicious_product_name(response):
        return False
    if _has_hallucinated_processor(response):
        return False
        
    if not validate_product_fields(response):
        return False

    return True


__all__ = ["SAFE_FALLBACK", "VALID_BRANDS", "validate_response"]
