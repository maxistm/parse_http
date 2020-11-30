import os
import time
import datetime as dt
import requests
import bs4
import pymongo
import dotenv
from urllib.parse import urljoin
import datetime


dotenv.load_dotenv(os.path.dirname(__file__)+'\\.env')


class MagnitParse:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:83.0) Gecko/20100101 Firefox/83.0'
    }

    

    def __init__(self, start_url):
        self.start_url = start_url
        connection_string = os.getenv('DATA_BASE')
        client = pymongo.MongoClient(connection_string)
        self.db = client['gb_parse_11']

        self.product_template = {
            'url': lambda soup: urljoin(self.start_url, soup.get('href')),
            'promo_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__title'}).text,
            'image_url': lambda soup: urljoin(self.start_url, soup.find('img').get('data-src')),
            'old_price': lambda soup: self.parse_price(soup, 'old'),
            'new_price': lambda soup: self.parse_price(soup, 'new'),
            'date_from': lambda soup: self.parse_date(soup, 1),
            'date_to': lambda soup: self.parse_date(soup, 2)

        }

    @staticmethod
    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise Exception
                return response
            except Exception:
                time.sleep(0.5)

    def soup(self, url) -> bs4.BeautifulSoup:
        response = self._get(url, headers=self.headers)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self.soup(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def parse_price(self, soup, key):
        soup_price = soup.find('div', attrs={'class': 'label__price_'+key})
        try:
            price = float(soup_price.find('span', attrs={'class':'label__price-integer'}).text + '.' + soup_price.find('span', attrs={'class':'label__price-decimal'}).text)
        except:
            price = None

        return price
    
     


    def parse_date(self, soup, fromto):
        months = dict(января=1, февраля=2, марта=3, апреля=4, мая=5, июня=6, июля=7, августа=8, сентября=9, октября=10, ноября=11, декабря=12)
        date_text = soup.find('div', attrs={'class': 'card-sale__date'}).text
        only = 0
        if 'только' in date_text:
            fromto = 1
            only = 1
        date_text = date_text.split('\n')[fromto]

        day = int(date_text.split()[1])
        mounth = months[date_text.split()[2]]
        year = datetime.datetime.today().year
        result_date = datetime.datetime(year, mounth, day)
        if (fromto == 2 or only == 1) and result_date < datetime.datetime.today():
            result_date = datetime.datetime(result_date.year + 1, result_date.month, result_date.day)
        return result_date

    def parse(self, soup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.find_all('a', recursive=False):
            pr_data = self.get_product(product)
            yield pr_data

    def get_product(self, product_soup) -> dict:

        result = {}
        for key, value in self.product_template.items():
            try:
                result[key] = value(product_soup)
            except Exception as e:
                continue
        return result

    def save(self, product):
        collection = self.db['magnit_11']
        collection.insert_one(product)


if __name__ == '__main__':
    parser = MagnitParse('https://magnit.ru/promo/?geo=moskva')
    parser.run()
