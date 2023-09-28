import json
from in_class import Crawler
from Homework import ProductInfoExtractor

def main() -> None:
    # Initialize the Crawler and ProductInfoExtractor
    crawler = Crawler()
    product_info_extractor = ProductInfoExtractor()

    # Define the URL and parameters for link extraction
    url = "https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776"
    pagesToProcess = 10
    pageStart = 1

    # Get links from the Crawler
    links = []
    for link in crawler.getItemsFromCategory(url, pageStart, pagesToProcess):
        print(link)
        links.append(link)

    # Save links to a text file
    with open("product_links.txt", "w") as file:
        for link in links:
            file.write(link + "\n")

    print(f"Total {len(links)} links saved to 'product_links.txt'")

    # Choose a single URL to extract information from
    url_to_extract = links[0]  # Change this to the index of the URL you want to extract

    # Extract information from the selected URL
    product_info = product_info_extractor.extractInfoFromPage(url_to_extract)
    
    product_info, extracted_url = product_info_extractor.extractInfoFromPage(url_to_extract)
    print("Extracted from URL:", extracted_url)
    if product_info:
        # Save extracted information to JSON for the selected URL
        with open("product_info.json", "w") as json_file:
            json.dump(product_info, json_file, indent=4)
        print(f"Extracted information saved to 'product_info.json'")

if __name__ == "__main__":
    main()
