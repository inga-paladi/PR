import requests
import validators
from bs4 import BeautifulSoup
import pika
from tinydb import TinyDB, Query
import threading


class Crawler:
    def __init__(self):
        self.db = TinyDB('products_db.json')
        
    def getItemsFromCategory(self, urlCategory: str, pageNr: int, pagesToProcessMore: int) -> [str]:
        foundUrls = set()
        pageUrl = urlCategory + "?page=" + str(pageNr)

        productsLinks = self.getNonBoostedProductLinksFromPage(pageUrl)
        if len(productsLinks) == 0:
            return []
        
        for productLink in productsLinks:
            foundUrls.add(productLink)

        if pagesToProcessMore != 0:
            for url in self.getItemsFromCategory(urlCategory, pageNr+1, pagesToProcessMore-1):
                foundUrls.add(url)
        
        return foundUrls

    def getNonBoostedProductLinksFromPage(self, url : str) -> [str]:
        response = requests.get(url)

        if response.status_code != 200:
            return []

        beautySoup = BeautifulSoup(response.text, 'html.parser')
        adsContainer = beautySoup.find(id="js-ads-container")
        nonBoostedAds = adsContainer.find('ul').find_all('li', {"class", "ads-list-photo-item"}) # the first unordered list is the one nonboosted

        links = set()
        for product in nonBoostedAds:
            try:
                if "js-booster-inline" in product['class']:
                    continue

                hrefValue = product.find('a').get('href')
                absPath = self.makeAbsPath(hrefValue)
                if (validators.url(absPath)):
                    links.add(absPath)
            except:
                pass

        return links
    
    def makeAbsPath(self, pathValue: str) -> str:
        if pathValue[0] != '/':
            return pathValue
        
        baseUrl = "https://999.md"
        return baseUrl + pathValue
    def push_links_to_queue(self, queue_name, links):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)

        for link in links:
            channel.basic_publish(exchange='', routing_key=queue_name, body=link)
            print(f" [x] Sent {link}")

        connection.close()

    def process_queue(self, queue_name, num_threads):
        def consumer():
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.queue_declare(queue=queue_name)

            def callback(ch, method, properties, body):
                print(f" [x] Received {body}")
                self.parse_product_details(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=queue_name, on_message_callback=callback)
            channel.start_consuming()

        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=consumer)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def parse_product_details(self, url):
        url_str = url.decode('utf-8')
        self.db.insert({'url': url_str})
        print(f"Link saved for {url_str}")
