"""Customer profile extractor using NLP heuristics.

Extracts:
- interests: client's areas of interest (e.g. gaming, developers, SaaS)
- preferred_brand: brands matching user choices (e.g. Apple, Samsung, Lenovo)
- budget: dollar amounts or ranges
- previous_products: products previously purchased or discussed
- previous_issues: problems/issues encountered by the user
- sentiment_history: list of past sentiment classifications
"""
import re
from typing import List, Dict, Any


def _find_currency(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"\$\s?[0-9,]+\b", text)
    if m:
        return m.group(0)
    m = re.search(r"([0-9,]+)\s?(usd|USD|dollars)\b", text)
    if m:
        return m.group(0)
    return ""


def _find_brands(text: str) -> str:
    lower = text.lower()
    brands = []
    if "apple" in lower or "iphone" in lower or "macbook" in lower:
        brands.append("Apple")
    if "samsung" in lower or "galaxy" in lower:
        brands.append("Samsung")
    if "lenovo" in lower or "legion" in lower:
        brands.append("Lenovo")
    if "dell" in lower or "xps" in lower:
        brands.append("Dell")
    if "nvidia" in lower or "geforce" in lower:
        brands.append("NVIDIA")
    if "intel" in lower:
        brands.append("Intel")
    return ", ".join(brands) if brands else ""


def extract_profile_from_messages(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Scan the conversation message history to build a persistent profile memory."""
    profile: Dict[str, Any] = {
        "interests": "",
        "preferred_brand": "",
        "budget": "",
        "previous_products": "",
        "previous_issues": "",
        "sentiment_history": []
    }

    # Aggregate text
    user_texts = []
    sentiments = []
    for m in messages:
        if m.get("role") == "user":
            user_texts.append(m.get("content", ""))
        if m.get("sentiment"):
            sentiments.append(m.get("sentiment"))

    full_text = " ".join(user_texts)
    lower_text = full_text.lower()

    # Extract budget
    budget = _find_currency(full_text)
    if budget:
        profile["budget"] = budget

    # Extract preferred brand
    brands = _find_brands(full_text)
    if brands:
        profile["preferred_brand"] = brands

    # Extract interests
    interests_list = []
    if "gaming" in lower_text:
        interests_list.append("Gaming Hardware")
    if "developer" in lower_text or "coding" in lower_text:
        interests_list.append("Software Development")
    if "saas" in lower_text or "cloud" in lower_text:
        interests_list.append("Cloud Solutions")
    if "market" in lower_text or "analytics" in lower_text:
        interests_list.append("Market Analysis")
    if "vulnerabilit" in lower_text or "security" in lower_text:
        interests_list.append("Cybersecurity")

    # Capture phrases after 'interested in'
    m_interest = re.findall(r"interested in\s+([a-zA-Z0-9\-\s]{3,30})", full_text, flags=re.I)
    for match in m_interest:
        clean_match = match.strip().title()
        if clean_match not in interests_list:
            interests_list.append(clean_match)

    if interests_list:
        profile["interests"] = ", ".join(interests_list)

    # Extract previous products mentioned as owned or evaluated
    prods = []
    m_prod = re.findall(r"(?:evaluating|using|purchased|bought|own|owns|use)\s+([a-zA-Z0-9\-\s]{3,30})", full_text, flags=re.I)
    for match in m_prod:
        clean_prod = match.strip().title()
        # Filter out common verbs
        if not any(v in clean_prod.lower() for v in ("you", "it", "the", "a", "this", "our")):
            prods.append(clean_prod)
    if prods:
        profile["previous_products"] = ", ".join(prods)

    # Extract previous issues (e.g. data corruption, latency, refund, warranty)
    issues = []
    if "corrupt" in lower_text:
        issues.append("Data Corruption")
    if "latency" in lower_text or "slow" in lower_text:
        issues.append("Latency Issues")
    if "refund" in lower_text or "cancel" in lower_text:
        issues.append("Billing/Refund Claim")
    if "broke" in lower_text or "fail" in lower_text:
        issues.append("System Deployment Failure")
    if "error" in lower_text or "bug" in lower_text:
        issues.append("Software Bug")
        
    m_issue = re.findall(r"(?:issue|problem|bug|failure)\s+with\s+([a-zA-Z0-9\-\s]{3,30})", full_text, flags=re.I)
    for match in m_issue:
        clean_issue = match.strip().title()
        if clean_issue not in issues:
            issues.append(clean_issue)

    if issues:
        profile["previous_issues"] = ", ".join(issues)

    # Sentiment history
    profile["sentiment_history"] = sentiments

    return {k: v for k, v in profile.items() if v}


__all__ = ["extract_profile_from_messages"]
