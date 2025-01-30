import re
from urllib.parse import urlparse

def validate_and_normalize_url(url: str) -> str | None:
    """
    Validates and normalizes a URL. Ensures the URL includes both a scheme (e.g., https)
    and a valid domain with a TLD. Returns the normalized URL or None if invalid.
    """
    # Helper function to validate TLDs
    if not _has_valid_tld(url):
        return None

    # Ensure the URL has a scheme, defaulting to HTTPS if missing
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"  # Assume HTTPS if the scheme is missing
    parsed = urlparse(url)  # Re-parse after potentially adding a scheme

    # Ensure the URL includes a valid netloc (domain)
    if not parsed.netloc or not _is_valid_domain(parsed.netloc):
        return None

    return url


def _has_valid_tld(url: str) -> bool:
    """
    Check if the URL includes a valid TLD (e.g., .com, .net, .org, .dev).
    """
    # Regex for valid TLDs (this can be extended with more TLDs if needed)
    tld_pattern = r"\.[a-zA-Z]{2,}$"  # Matches TLDs like .com, .io, .dev
    return bool(re.search(tld_pattern, urlparse(url).netloc or url))


def _is_valid_domain(domain: str) -> bool:
    """
    Check if the domain contains valid components (e.g., no spaces, only valid characters).
    """
    # Regex for a valid domain name
    domain_pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    return bool(re.match(domain_pattern, domain)) # Return None if no valid domain is found