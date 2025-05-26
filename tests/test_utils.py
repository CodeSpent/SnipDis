import pytest
from bot.util import (
    extract_youtube_video_id,
    validate_and_normalize_url,
    truncate_string,
    remove_website_title,
    get_domain_from_url
)


# Test cases for YouTube video ID extraction
@pytest.mark.parametrize("url,expected", [
    # Standard youtube.com URLs
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),

    # URLs with additional parameters
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=shared", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLsome_list", "dQw4w9WgXcQ"),

    # Short youtu.be URLs
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ?t=123", "dQw4w9WgXcQ"),

    # Invalid URLs
    ("https://youtube.com/watch", None),
    ("https://youtu.be/", None),
    ("https://example.com", None),
    ("", None),
])
def test_extract_youtube_video_id(url, expected):
    assert extract_youtube_video_id(url) == expected


# Test cases for URL validation and normalization
@pytest.mark.parametrize("url,expected", [
    ("example.com", "https://example.com"),
    ("https://example.com", "https://example.com"),
    ("http://example.com", "http://example.com"),
    ("invalid url", None),
    ("example", None),
    ("", None),
])
def test_validate_and_normalize_url(url, expected):
    assert validate_and_normalize_url(url) == expected


# Test string truncation
@pytest.mark.parametrize("input_str,max_length,expected", [
    ("Short string", 20, "Short string"),
    ("This is a very long string", 10, "This is..."),
    ("", 10, ""),
    ("Test", 3, "..."),
])
def test_truncate_string(input_str, max_length, expected):
    assert truncate_string(input_str, max_length) == expected


# Test website title removal
@pytest.mark.parametrize("title,url,expected", [
    ("Article Title - example.com", "https://example.com", "Article Title"),
    ("Pure Title", "https://example.com", "Pure Title"),
    ("Title | Website.com", "https://website.com", "Title"),
    ("", "https://example.com", ""),
])
def test_remove_website_title(title, url, expected):
    result = remove_website_title(title, url)
    assert result.strip() == expected


# Test domain extraction
@pytest.mark.parametrize("url,expected", [
    ("https://www.example.com", "example.com"),
    ("http://subdomain.example.com", "subdomain.example.com"),
    ("example.com", "example.com"),
    ("invalid-url", None),
    ("", None),
])
def test_get_domain_from_url(url, expected):
    assert get_domain_from_url(url) == expected