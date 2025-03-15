import os
import re
from urllib.parse import urlparse, urlencode
import aiohttp
from bot.config import DEV_GUILD_ID
from typing import List

def validate_and_normalize_url(url: str) -> str | None:
    """
    Validates and normalizes a URL. Ensures the URL includes both a scheme (e.g., https)
    and a valid domain with a TLD. Returns the normalized URL or None if invalid.
    """
    if not _has_valid_tld(url):
        return None

    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
    parsed = urlparse(url)

    if not parsed.netloc or not _is_valid_domain(parsed.netloc):
        return None

    return url


def truncate_string(input_str: str, max_length: int = 100) -> str:
    """
    Truncates a string to a specified maximum length.

    Args:
        input_str (str): The input string to truncate.
        max_length (int): The maximum allowed length of the string.

    Returns:
        str: The truncated string, with '...' appended if it was shortened.
    """
    if len(input_str) > max_length:
        return input_str[:max_length - 3] + "..."
    return input_str


def _has_valid_tld(url: str) -> bool:
    """
    Check if the URL includes a valid TLD (e.g., .com, .net, .org, .dev).
    """
    tld_pattern = r"\.[a-zA-Z]{2,}$"
    return bool(re.search(tld_pattern, urlparse(url).netloc or url))


def _is_valid_domain(domain: str) -> bool:
    """
    Check if the domain contains valid components (e.g., no spaces, only valid characters).
    """
    domain_pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    return bool(re.match(domain_pattern, domain))


def remove_website_title(title: str, url: str) -> str:
    """
    Removes references to the website's name or domain from a title.

    Args:
        title (str): The input title to clean.
        url (str): The website URL to check for its domain.

    Returns:
        str: The title with the website name removed.
    """
    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split('.')

        filtered_parts = [part for part in domain_parts if part not in ['www']]
        if len(filtered_parts) > 1:
            base_name = filtered_parts[-2]
        else:
            base_name = filtered_parts[0]

        patterns = [re.escape(base_name), re.escape('.'.join(filtered_parts))]

        clean_title = re.sub(rf"\b(?:{'|'.join(patterns)})\b", '', title, flags=re.IGNORECASE).strip()
        clean_title = re.sub(r"[-|:_]+$", '', clean_title).strip()

        return clean_title
    except Exception as e:
        print(f"Error cleaning title: {e}")
        return title


def get_guild_ids_for_environment():
    if DEV_GUILD_ID:
        return [int(DEV_GUILD_ID)]
    return None


async def fetch_proxies() -> List[str]:
    """
    Fetch a list of proxies from the ProxyScrape API.
    The URL is built dynamically with parameters for flexibility.

    Returns:
        List[str]: List of proxies fetched from the API.
    """
    try:
        base_url = "https://api.proxyscrape.com/v2/account/datacenter_shared/proxy-list"
        api_key = os.getenv("PROXYSCRAPE_API_KEY")

        if not api_key:
            raise ValueError("ProxyScrape API Key is missing.")

        params = {
            "auth": api_key,
            "type": "getproxies",
            "country[]": "all",
            "protocol": "http",
            "format": "normal",
            "status": "all",
        }

        query_string = urlencode(params, doseq=True)
        url = f"{base_url}?{query_string}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    proxy_list = await response.text()
                    return proxy_list.strip().split("\n")
                else:
                    print(f"Failed to fetch proxies. HTTP Status Code: {response.status}")
                    return []
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        return []