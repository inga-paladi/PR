import json
from crawler import Crawler

def main() -> None:
    # Initialize the Crawler and ProductInfoExtractor
    crawler = Crawler()

    # Define the URL and parameters for link extraction
    url = "https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776"
    pagesToProcess = 10
    pageStart = 1

    # Get links from the Crawler
    links = list(crawler.getItemsFromCategory(url, pageStart, pagesToProcess))
    crawler.push_links_to_queue('product_links_queue', links)

    num_threads = 4  # Number of concurrent consumers
    crawler.process_queue('product_links_queue', num_threads)

if __name__ == "__main__":
    main()