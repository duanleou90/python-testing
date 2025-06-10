#!/usr/bin/env python3
"""
Simple Google Search App
A command-line application that searches Google and displays the first 5 URLs.
"""

import requests
import json
import sys
from typing import Optional, List


class GoogleSearchApp:
    def __init__(self, api_key: str, search_engine_id: str):
        """
        Initialize the Google Search App

        Args:
            api_key: Your Google API key
            search_engine_id: Your Custom Search Engine ID
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 5) -> Optional[List[str]]:
        """
        Search Google and return URLs

        Args:
            query: Search term
            num_results: Number of results to return (max 10)

        Returns:
            List of URLs or None if error
        """
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(num_results, 10)  # API max is 10
        }

        try:
            print(f"Searching for: '{query}'...")
            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Extract URLs from results
                urls = []
                items = data.get('items', [])

                if not items:
                    print("No results found.")
                    return []

                for item in items:
                    urls.append(item.get('link', ''))

                return urls

            elif response.status_code == 403:
                print("Error: API key invalid or quota exceeded.")
                print("Please check your API key and make sure you haven't exceeded the daily limit.")

            elif response.status_code == 429:
                print("Error: Too many requests. Please wait and try again.")

            else:
                print(f"Error {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            print("Error: Unable to connect to Google API. Check your internet connection.")
        except requests.exceptions.Timeout:
            print("Error: Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
        except json.JSONDecodeError:
            print("Error: Invalid response from Google API.")

        return None

    def run(self):
        """Run the interactive search application"""
        print("=" * 50)
        print("      GOOGLE SEARCH APP")
        print("=" * 50)
        print()

        while True:
            try:
                # Get search term from user
                search_term = input("Enter search term (or 'quit' to exit): ").strip()

                if not search_term:
                    print("Please enter a search term.")
                    continue

                if search_term.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                # Perform search
                urls = self.search(search_term)

                if urls:
                    print(f"\nFirst {len(urls)} results:")
                    print("-" * 40)

                    for i, url in enumerate(urls, 1):
                        print(f"{i}. {url}")

                    print("-" * 40)

                print()  # Empty line for readability

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")


def main():
    """Main function to run the application"""
    # Configuration - Replace with your actual credentials
    API_KEY = ""
    SEARCH_ENGINE_ID = ""

    # Check if credentials are set
    if API_KEY == "YOUR_API_KEY_HERE" or SEARCH_ENGINE_ID == "YOUR_SEARCH_ENGINE_ID_HERE":
        print("Error: Please set your API_KEY and SEARCH_ENGINE_ID")
        print("\nTo get these credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Custom Search API")
        print("3. Create an API key in Credentials")
        print("4. Create a Custom Search Engine at https://cse.google.com/cse/")
        print("5. Update the API_KEY and SEARCH_ENGINE_ID variables in this script")
        sys.exit(1)

    # Create and run the app
    app = GoogleSearchApp(API_KEY, SEARCH_ENGINE_ID)
    app.run()


if __name__ == "__main__":
    main()


# Alternative version with command line arguments
def run_with_args():
    """Alternative version that accepts command line arguments"""
    if len(sys.argv) < 4:
        print("Usage: python search_app.py <API_KEY> <SEARCH_ENGINE_ID> <SEARCH_TERM>")
        sys.exit(1)

    api_key = sys.argv[1]
    search_engine_id = sys.argv[2]
    search_term = " ".join(sys.argv[3:])  # Join remaining args as search term

    app = GoogleSearchApp(api_key, search_engine_id)
    urls = app.search(search_term)

    if urls:
        print(f"First {len(urls)} results for '{search_term}':")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
    else:
        print("No results found or error occurred.")

# Uncomment the line below if you prefer command line arguments
# run_with_args()