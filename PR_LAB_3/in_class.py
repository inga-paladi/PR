import requests
import validators
from bs4 import BeautifulSoup

class Crawler:
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