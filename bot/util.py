import os
import re
from urllib.parse import urlparse, urlencode, parse_qs
import aiohttp
import discord
from bot.config import DEV_GUILD_IDS
from typing import List, Optional, Callable
import asyncio
import requests
from bs4 import BeautifulSoup
from services.youtube import YouTubeService

youtube_service = YouTubeService(os.getenv("YOUTUBE_API_KEY"))

def validate_and_normalize_url(url: str) -> str | None:
    """
    Validates and normalizes a URL. Ensures the URL includes both a scheme (e.g., https)
    and a valid domain with a TLD. Returns the normalized URL or None if invalid.
    """
    # Check for valid TLD
    if not _has_valid_tld(url):
        return None

    # Parse the URL
    parsed = urlparse(url)
    if not parsed.scheme:  # If no scheme, assume 'https://'
        url = f"https://{url}"
    parsed = urlparse(url)

    # Validate domain
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


def extract_youtube_video_id(url: str) -> str | None:
    """
    Extract the video ID from a YouTube URL, supporting both 'youtube.com' and 'youtu.be' formats.
    Strips all additional query parameters to ensure only the video ID is returned.

    Args:
        url (str): The YouTube URL.

    Returns:
        str | None: The extracted video ID, or None if it can't be determined.
    """
    parsed_url = urlparse(url)

    if "youtube.com" in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0]
        return video_id if video_id else None

    if "youtu.be" in parsed_url.netloc:
        # Extract the path and remove any query parameters
        video_id = parsed_url.path.lstrip("/")
        if not video_id:
            return None
        # Split on the first occurrence of '?' and take the first part
        return video_id.split("?")[0] or None

    return None

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
        domain_parts = parsed_url.netloc.lower().split('.')
        
        # Filter out common prefixes and get domain parts
        filtered_parts = [part for part in domain_parts if part not in ['www']]
        patterns = []
        
        # Add all possible domain combinations to patterns
        for i in range(len(filtered_parts)):
            pattern = '.'.join(filtered_parts[i:])
            patterns.append(re.escape(pattern))
        
        # Create pattern for common separators
        separators = '[-|:_]'
        pattern = f"\\s*{separators}\\s*(?:{'|'.join(patterns)})\\s*$"
        
        # Remove domain and separators
        clean_title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        return clean_title.strip()
    except Exception as e:
        print(f"Error cleaning title: {e}")
        return title


def get_guild_ids_for_environment():
    """
    Retrieves a list of guild IDs for the current environment.

    Note: This is currently only used for development environments.

    Returns:
        list[int] | None: A list of integer guild IDs or None if no guild IDs are provided.
    """
    if DEV_GUILD_IDS:
        # Split the comma-delimited string into an array and convert each ID to an integer
        return [int(guild_id.strip()) for guild_id in DEV_GUILD_IDS.split(",")]
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


async def fetch_youtube_video_title(url: str) -> Optional[str]:
    """
    Fetches the title of a YouTube video using its URL via the YouTubeService.

    Parameters:
        url (str): The URL of the YouTube video. It should be a valid YouTube URL either in
                   "youtu.be" short format or "youtube.com/watch" format.

    Returns:
        Optional[str]: The YouTube video title if retrieved successfully, otherwise None.
    """
    video_id = extract_youtube_video_id(url)

    try:
        title = youtube_service.get_video_title(video_id)
        return title if "No video found" not in title and "An error occurred" not in title else None
    except Exception as e:
        print(f"Error fetching YouTube video title from service: {e}")
        return None


async def fetch_webpage_title(url: str, retries: int = 1) -> Optional[str]:
    """
    Fetches the webpage title from the given URL.

    This function attempts to retrieve the webpage's title by first determining
    if the URL requires a specific domain handler. If a custom domain handler
    is found, it is used to process the URL. If not, the function sends an HTTP
    GET request to the URL and parses the HTML content to extract the title.

    It searches for titles defined in the `<title>` tag, as well as meta tags
    `og:title` and `twitter:title`. The longest title among these is selected.

    If a failure occurs (e.g., non-200 status code, network issues), the function
    retries up to the specified number of attempts, pausing briefly between retries.

    Parameters:
        url (str): The webpage URL to fetch the title from.
        retries (int): The number of attempts to fetch the title. Default is 3.

    Returns:
        Optional[str]: The extracted longest title if found; otherwise, None.
    """
    for attempt in range(retries):
        try:
            domain_handler = get_domain_handler(url)
            if domain_handler:
                return await domain_handler(url)

            response = requests.get(url)
            if response.status_code != 200:
                print(f"Attempt {attempt + 1}/{retries} failed: Status Code {response.status_code}")
                continue

            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")

            titles = []

            if soup.title and soup.title.string:
                titles.append(soup.title.string.strip())

            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                titles.append(og_title["content"].strip())

            twitter_title = soup.find("meta", property="twitter:title")
            if twitter_title and twitter_title.get("content"):
                titles.append(twitter_title["content"].strip())

            longest_title = max(titles, key=len, default=None)
            if longest_title:
                print(f"Longest title found: {longest_title}")
                return longest_title

        except Exception as e:
            print(f"Attempt {attempt + 1}/{retries} failed due to error: {e}")
            await asyncio.sleep(1)

    print("Failed to fetch a valid title after retries.")
    return None


def get_domain_from_url(url: str) -> Optional[str]:
    """
    Extract the domain name from a given URL.

    This function takes a URL as input and extracts the domain name from it.
    It uses a regular expression to parse the URL and identify the domain.
    If the URL is invalid or the domain cannot be extracted, the function
    returns None.

    Args:
        url (str): A string representing the URL from which to extract
                   the domain.

    Returns:
        Optional[str]: The domain name extracted from the URL, or None if
                       the domain cannot be identified.
    """
    regex = r"(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

    match = re.search(regex, url)
    if match:
        domain = match.group(1)
        return domain
    return None


def get_domain_handler(url: str) -> Optional[Callable[[str], Optional[str]]]:
    """
    Retrieve a domain handler function for the provided URL.

    This function extracts the domain from the given URL and searches for a
    predefined handler function associated with the domain. If a matching
    handler is found, it returns the callable handler function. Otherwise,
    it returns None.

    Parameters:
        url (str): The URL from which to determine a domain-specific handler.

    Returns:
        Optional[Callable[[str], Optional[str]]]: A callable handler function
        if a matching domain is found; otherwise, None.
    """
    domain = get_domain_from_url(url)
    if not domain:
        return None

    for registered_domain, extractor_name in DOMAIN_EXTRACTORS.items():
        if registered_domain in domain:
            extractor_function = globals().get(extractor_name)
            if callable(extractor_function):
                return extractor_function

    return None


def build_mentioned_users_string(mention: discord.User, additional_mentions: List[discord.User]) -> str:
    """
    Builds a concatenated string of mentioned users for a message or embed.

    This function takes a primary mentioned user and a list of additional
    mentioned users, and builds a comma-separated string of their
    usernames.

    Parameters:
        mention (discord.User): The initially mentioned user.
        additional_mentions (List[discord.User]): A list of additional mentioned users.

    Returns:
        str: Comma-delimited string of mentioned users.
    """
    if not mention:
        raise ValueError("Initial mention user is required.")

    """
    The way mentions work due to limitations of autocomplete functionality
    is that we allow one mention to be inline using autocomplete as `mention`,
    but all subsequent mentions are in a standard text field comma-delimited.

    I would like to have multiple mentions in the autocomplete field, but
    to my knowledge this is not yet possible.
    """
    mentions = []

    if mention:
        mentions.append(mention)

    if additional_mentions:
        mentions.extend(additional_mentions)

    mentions_string = ", ".join(
        [f"<@{mention}>" if isinstance(mention, str) else f"<@{mention.id}>" for mention in mentions])
    return mentions_string



def convert_string_id_to_discord_member(ctx: discord.ApplicationContext, user_id: str) -> discord.User | None:
    user_id = user_id.strip().strip('<!@>')
    member = ctx.guild.get_member(int(user_id))
    return member