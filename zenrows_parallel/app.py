import requests
import sys
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor


def is_valid_url(url):
    """Check if the provided URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_web_content_zenrows(url, api_key):
    """
    Fetch web content using ZenRows API
    You need to sign up at https://zenrows.com/ to get an API key
    """
    zenrows_url = "https://api.zenrows.com/v1/"

    params = {
        'url': url,
        'apikey': api_key,
        'js_render': 'true',  # Enable JavaScript rendering
        'premium_proxy': 'true'  # Use premium proxies
    }

    try:
        response = requests.get(zenrows_url, params=params, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching content from {url}: {str(e)}"


def get_urls_from_user():
    """Get 3 URLs from the user with validation"""
    urls = []

    print("Please enter 3 URLs:")
    for i in range(3):
        while True:
            url = input(f"Enter URL #{i + 1}: ").strip()

            if not url:
                print("Please enter a valid URL.")
                continue

            # Add https:// if no scheme is provided
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            if is_valid_url(url):
                urls.append(url)
                break
            else:
                print("Invalid URL format. Please try again.")

    return urls


def fetch_multiple_urls_parallel(urls, api_key):
    """
    Fetch content from multiple URLs in parallel using ZenRows
    """

    def fetch_single_url(url):
        print(f"Starting fetch for: {url}")
        start_single = time.time()
        result = get_web_content_zenrows(url, api_key)
        end_single = time.time()
        print(f"Completed fetch for: {url} in {end_single - start_single:.2f} seconds")
        return result

    start_time = time.time()
    print("Submitting all URLs for parallel processing...")

    # Use ThreadPoolExecutor for true parallel execution
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks immediately - this starts parallel execution
        futures = {url: executor.submit(fetch_single_url, url) for url in urls}
        results = {}

        # Collect results as they complete (this preserves parallel execution)
        from concurrent.futures import as_completed
        for future in as_completed(futures.values()):
            # Find which URL this future corresponds to
            for url, fut in futures.items():
                if fut == future:
                    try:
                        content = future.result()
                        results[url] = content
                    except Exception as e:
                        results[url] = f"Error fetching {url}: {str(e)}"
                    break

    end_time = time.time()
    print(f"\nAll URLs fetched in {end_time - start_time:.2f} seconds")

    return results


def display_results(results):
    """Display content from all URLs"""
    for i, (url, content) in enumerate(results.items(), 1):
        print(f"\n{'=' * 80}")
        print(f"CONTENT FROM URL #{i}: {url}")
        print(f"{'=' * 80}")

        if content.startswith("Error"):
            print(content)
        else:
            # Limit output for readability (first 1500 characters per URL)
            if len(content) > 1500:
                print(content[:1500])
                print(f"\n... (Content truncated. Total length: {len(content)} characters)")
            else:
                print(content)

        print(f"{'=' * 80}")


def main():
    print("Parallel Web Content Fetcher with ZenRows")
    print("=" * 45)

    # Get ZenRows API key first
    api_key = input("Enter your ZenRows API key: ").strip()
    if not api_key:
        print("Error: ZenRows API key is required to use this application.")
        print("Please sign up at https://zenrows.com/ to get your API key.")
        sys.exit(1)

    # Get 3 URLs from user
    urls = get_urls_from_user()

    print(f"\nURLs to fetch:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")

    print("-" * 60)
    print(f"\nFetching content from {len(urls)} URLs using ZenRows API...")
    print("This may take a few moments...")

    # Fetch all URLs in parallel using ZenRows
    results = fetch_multiple_urls_parallel(urls, api_key)

    # Display all results
    display_results(results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)