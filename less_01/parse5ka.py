import os
from pathlib import Path
import json
import time

import requests


class Parse5ka:
    _headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:82.0) Gecko/20100101 Firefox/82.0",
    }
    _params = {
        'records_per_page': 50,
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self.catalog_url = 'https://5ka.ru/api/v2/categories/'

    @staticmethod
    def _get(*args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    # todo Создать класс исключение
                    raise Exception
                return response
            except Exception:
                time.sleep(0.25)

    def parse_catalogs(self, url):
        #params = self._params
        response: requests.Response = self._get(url, headers=self._headers)
        data = response.json()
        return data


    def parse(self, url, cat = ""):
        params = self._params
        params['categories'] = cat
        while url:
            response: requests.Response = self._get(url, params=params , headers=self._headers)
            if params:
                params = {}
            data: dict = response.json()
            url = data.get('next')
            yield data.get('results')

    def run(self):
        catalog_dict = self.parse_catalogs(self.catalog_url)

        for category in catalog_dict:
            category['products'] = []
            for products in self.parse(self.start_url, category['parent_group_code']):
                for product in products:
                    category['products'].append(product)
                time.sleep(0.1)
            if len(category['products']) > 0:
                self._save_to_file(category)

    @staticmethod
    def _save_to_file(category):
        path = Path(os.path.dirname(__file__)).joinpath('products').joinpath(f'{category["parent_group_code"]}.json')
        with open(path, 'w', encoding='UTF-8') as file:
            json.dump(category, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parse5ka('https://5ka.ru/api/v2/special_offers/')
    parser.run()
