import requests
from bs4 import BeautifulSoup
import validators

class ProductInfoExtractor:
    def extractInfoFromPage(self, url):
        baseUrl = "https://999.md"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        info = {}

        def extract_key_value_pairs(ul, key_class, value_class):
            pairs = {}
            for li in ul.find_all('li', class_=key_class):
                key = li.find('span', class_='adPage__content__features__key').text.strip()
                value = li.find('span', class_=value_class).text.strip()
                pairs[key] = value
            return pairs

        for groupTitle in ['Caracteristici', 'Condiții de utilizare', 'Adăugător', 'Subcategorie', 'Preț', 'Regiunea', 'Contacte']:
            section = soup.find('h2', string=groupTitle)
            
            if section or groupTitle in ['Preț', 'Regiunea', 'Contacte']:
                info[groupTitle] = {}
                
                if groupTitle == 'Caracteristici':
                    info[groupTitle] = extract_key_value_pairs(section.find_next('ul'), 'm-value', 'adPage__content__features__value')
                elif groupTitle == 'Condiții de utilizare':
                    info[groupTitle] = extract_key_value_pairs(section.find_next('ul'), 'm-value', 'adPage__content__features__key with-rules')
                elif groupTitle == 'Adăugător':
                    info[groupTitle] = {li.find('span', class_='adPage__content__features__key').text.strip(): None for li in section.find_next('ul').find_all('li', class_='m-no_value')}
                elif groupTitle == 'Subcategorie':
                    info[groupTitle] = baseUrl + soup.find("a", class_="adPage__content__features__category__link").get('href')
                elif groupTitle == 'Preț':
                    key = ''
                    prices = {}
                    for ul in soup.find_all('ul', {'class': 'adPage__content__price-feature__prices'}):
                        for li in ul.find_all('li', class_=lambda x: x not in [['tooltip', 'adPage__content__price-feature__prices__price', 'is-main'], ['tooltip', 'adPage__content__price-feature__prices__price']]):
                            value = li.find('span', class_='adPage__content__price-feature__prices__price__value').text.strip()
                            currency = li.find('span', class_='adPage__content__price-feature__prices__price__currency').text.strip()
                            value += ' ' + currency
                            
                            if currency in ('€', 'lei', '$'):
                                key = {'€': 'Euro', 'lei': 'Lei', '$': 'USD'}.get(currency)
                                prices[key] = value
                    info[groupTitle] = prices
                elif groupTitle == 'Regiunea':
                    address = ''.join(v.text.strip() for v in soup.findAll('dd', {'itemprop': 'address'}))
                    info[groupTitle] = address
                elif groupTitle == 'Contacte':
                    value = soup.find('dt', string=groupTitle + ': ')
                    if not value:
                        info[groupTitle] = None
                    else:
                        contact_info = value.find_next('dd').find_next('ul').find_next('li').find('a')
                        info[groupTitle] = contact_info.get('href') if contact_info else None

        return info, url
