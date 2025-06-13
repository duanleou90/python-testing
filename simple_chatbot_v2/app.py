import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class QuestionAnsweringApp:
    def __init__(self, openai_api_key, google_api_key, google_cse_id, zenrows_api_key):
        """
        Initialize the app with necessary API keys

        Args:
            openai_api_key: Your OpenAI API key
            google_api_key: Your Google API key
            google_cse_id: Your Google Custom Search Engine ID
            zenrows_api_key: Your ZenRows API key
        """
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        self.zenrows_api_key = zenrows_api_key
        self.print_lock = threading.Lock()

    def thread_safe_print(self, message):
        """Print messages safely in multi-threaded environment"""
        with self.print_lock:
            print(message)

    def generate_search_term(self, question):
        """Generate an optimized search term from the user's question"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system",
                     "content": "You are a search query optimizer. Convert the user's question into an effective Google search query. Return only the search query, nothing else."},
                    {"role": "user", "content": question}
                ],
                max_tokens=50,
                temperature=0.3
            )
            search_term = response.choices[0].message.content.strip()
            print(f"\nGenerated search term: {search_term}")
            return search_term
        except Exception as e:
            print(f"Error generating search term: {e}")
            return question  # Fallback to original question

    def google_search(self, search_term, num_results=5):
        """Perform Google Custom Search and return top results"""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': search_term,
                'num': num_results
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            results = response.json()
            search_results = []

            if 'items' in results:
                for item in results['items']:
                    search_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })

            return search_results
        except Exception as e:
            print(f"Error performing Google search: {e}")
            return []

    def crawl_content_zenrows(self, url, max_length=9000):
        """Crawl content from a URL using ZenRows for JS rendering"""
        try:
            zenrows_url = "https://api.zenrows.com/v1/"

            params = {
                'url': url,
                'apikey': self.zenrows_api_key,
                'js_render': 'true',  # Enable JavaScript rendering
                'wait': '3000',  # Wait 3 seconds for JS to load
                'premium_proxy': 'true',  # Use premium proxies for better success rate
                'antibot': 'true'  # Enable anti-bot detection bypass
            }

            response = requests.get(zenrows_url, params=params, timeout=30)
            response.raise_for_status()

            # Check if we got HTML content
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Get text content
                text = soup.get_text()

                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                # Limit text length
                if len(text) > max_length:
                    text = text[:max_length] + "..."

                return text
            else:
                return f"Failed to retrieve content: HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            return "Timeout: Page took too long to load"
        except Exception as e:
            return f"Error crawling: {str(e)}"

    def crawl_single_url(self, index, result, total):
        """Helper function to crawl a single URL with timing"""
        self.thread_safe_print(f"Crawling {index + 1}/{total}: {result['title']}")
        start_time = time.time()
        content = self.crawl_content_zenrows(result['link'])
        crawl_time = time.time() - start_time
        self.thread_safe_print(f"  → [{index + 1}] Completed in {crawl_time:.2f} seconds")

        return {
            'title': result['title'],
            'url': result['link'],
            'text': content,
            'crawl_time': crawl_time,
            'index': index
        }

    def crawl_urls_parallel(self, search_results, max_workers=5):
        """Crawl multiple URLs in parallel"""
        reference_content = []
        total_start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all crawling tasks
            future_to_result = {
                executor.submit(self.crawl_single_url, i, result, len(search_results)): i
                for i, result in enumerate(search_results)
            }

            # Collect results as they complete
            for future in as_completed(future_to_result):
                try:
                    crawl_result = future.result()
                    reference_content.append(crawl_result)
                except Exception as e:
                    index = future_to_result[future]
                    self.thread_safe_print(f"  → [{index + 1}] Failed: {str(e)}")

        # Sort results by original index to maintain order
        reference_content.sort(key=lambda x: x['index'])

        total_time = time.time() - total_start_time
        print(f"\nTotal crawling time: {total_time:.2f} seconds (parallel execution)")

        return reference_content

    def get_answer_from_openai(self, question, reference_content):
        """Get answer from OpenAI using the question and reference content"""
        try:
            # Prepare the context
            context = "Use the following reference content to answer the question. If the answer cannot be found in the reference content, say so.\n\n"
            context += "Reference Content:\n"

            for i, content in enumerate(reference_content):
                if content['text'] and not content['text'].startswith(('Error', 'Failed', 'Timeout')):
                    context += f"\n--- Source {i + 1}: {content['title']} ---\n"
                    context += f"URL: {content['url']}\n"
                    context += f"Content: {content['text'][:9000]}...\n"  # Limit each source

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that answers questions based on provided reference content. Always cite your sources when answering."},
                    {"role": "user", "content": f"{context}\n\nQuestion: {question}"}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting answer from OpenAI: {e}")
            return "Sorry, I couldn't generate an answer due to an error."

    def run(self):
        """Main application loop"""
        print("Question Answering App with Web Search (ZenRows + Parallel Crawling)")
        print("=" * 70)

        while True:
            # Get question from user
            question = input("\nEnter your question (or 'quit' to exit): ").strip()

            if question.lower() == 'quit':
                print("Thanks for using the app!")
                break

            if not question:
                print("Please enter a valid question.")
                continue

            print(f"\nProcessing question: {question}")

            # Generate search term
            search_term = self.generate_search_term(question)

            # Search Google
            print("\nSearching Google...")
            search_results = self.google_search(search_term)

            if not search_results:
                print("No search results found.")
                continue

            # Crawl content from search results in parallel
            print(f"\nCrawling content from top {len(search_results)} results in parallel...")
            reference_content = self.crawl_urls_parallel(search_results)

            # Get answer from OpenAI
            print("\nGenerating answer...")
            answer = self.get_answer_from_openai(question, reference_content)

            # Print the answer
            print("\n" + "=" * 70)
            print("ANSWER:")
            print("=" * 70)
            print(answer)
            print("=" * 70)


def main():
    # Configuration
    # You need to set these environment variables or replace with your actual keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', '')
    ZENROWS_API_KEY = os.getenv('ZENROWS_API_KEY', '')

    if any('your-' in key for key in [OPENAI_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID, ZENROWS_API_KEY]):
        print("ERROR: Please set your API keys!")
        print("\nYou need to:")
        print("1. Get an OpenAI API key from https://platform.openai.com/api-keys")
        print("2. Get a Google API key from https://console.cloud.google.com/")
        print("3. Create a Custom Search Engine at https://programmablesearchengine.google.com/")
        print("4. Get a ZenRows API key from https://www.zenrows.com/")
        print("\nThen either:")
        print("- Set them as environment variables: OPENAI_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID, ZENROWS_API_KEY")
        print("- Or replace the placeholder values in the code")
        return

    # Create and run the app
    app = QuestionAnsweringApp(OPENAI_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID, ZENROWS_API_KEY)
    app.run()


if __name__ == "__main__":
    main()