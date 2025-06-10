import requests
import sys
from urllib.parse import urlparse


def is_valid_url(url):
    """Check if the provided URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_web_content_zenscrape(url, api_key):
    """
    Fetch web content using Zenscrape API
    You need to sign up at https://zenscrape.com/ to get an API key
    """
    zenscrape_url = "https://api.zenrows.com/v1/"

    params = {
        'url': url,
        'apikey': api_key,
        'js_render': 'true',
    }

    try:
        response = requests.get(zenscrape_url, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching content: {str(e)}"


def get_web_content_direct(url):
    """
    Alternative method: Direct HTTP request (fallback option)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching content: {str(e)}"


def main():
    print("Web Content Fetcher")
    print("=" * 30)

    # Get URL from user
    while True:
        url = input("\nEnter the URL you want to fetch: ").strip()

        if not url:
            print("Please enter a valid URL.")
            continue

        # Add http:// if no scheme is provided
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        if is_valid_url(url):
            break
        else:
            print("Invalid URL format. Please try again.")

    print(f"\nFetching content from: {url}")
    print("-" * 50)

    # Option 1: Using Zenscrape (requires API key)
    use_zenscrape = input("\nDo you want to use Zenscrape API? (y/n): ").lower().strip()

    if use_zenscrape == 'y':
        api_key = input("Enter your Zenscrape API key: ").strip()
        if api_key:
            content = get_web_content_zenscrape(url, api_key)
        else:
            print("No API key provided. Using direct method instead.")
            content = get_web_content_direct(url)
    else:
        # Option 2: Direct HTTP request (fallback)
        content = get_web_content_direct(url)

    # Display content
    print("\n" + "=" * 50)
    print("FETCHED CONTENT:")
    print("=" * 50)

    if content.startswith("Error"):
        print(content)
    else:
        # Limit output for readability (first 2000 characters)
        if len(content) > 2000:
            print(content[:2000])
            print(f"\n... (Content truncated. Total length: {len(content)} characters)")
        else:
            print(content)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)