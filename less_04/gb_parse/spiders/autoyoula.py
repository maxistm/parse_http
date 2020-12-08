import scrapy
import pymongo
import urllib
from urllib.parse import unquote
import json, re
import requests
import dotenv, os
import base64


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    ccs_query = {
        'brands': 'div.ColumnItemList_container__5gTrc div.ColumnItemList_column__5gjdt a.blackLink',
        'pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient(os.getenv('DATA_BASE'))['parse_gb_11'][self.name]

    def parse(self, response):
        for brand in response.css(self.ccs_query['brands']):
            if  'audi' in brand.attrib.get('href'):
                yield response.follow(brand.attrib.get('href'), callback=self.brand_page_parse)

    def brand_page_parse(self, response):
        for pag_page in response.css(self.ccs_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)

        for ads_page in response.css(self.ccs_query['ads']):
            yield response.follow(ads_page.attrib.get('href'), callback=self.ads_parse)

    def unquote_url(self, url):
        """Decodes a URL that was encoded using quote_url.
        Returns a unicode instance.
        """
        return urllib.parse.unquote(url)



    def ads_parse(self, response):
        try:
            data = {
                'title': response.css('.AdvertCard_advertTitle__1S1Ak::text').get(),
                'images': [img.attrib.get('src') for img in response.css('figure.PhotoGallery_photo__36e_r img')],
                'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').get(),
                'url': response.url,
                'autor': self.get_author(response),             
                'specification': self.get_specifications(response),
                'phone': self.get_phone(response)
            }
            

            self.db.insert_one(data)
            
        except Exception as e:
            print(e)
        

    def get_phone(self, response):
        
        #первый способ через мобильный вид:
        """
        mobile_header = {
                'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
                }
        request_object = requests.get(url = response.url, headers = mobile_header)
        response_object = scrapy.Selector(text = request_object.text)
        return response_object.css('.advert__call a').xpath('@href').get().replace('tel:','')
        """

        #второй подсказали декодировку

        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        re_str = re.compile(r"phone%22%2C%22([0-9|a-zA-Z]+)Xw%3D%3D%22%2C%22time")
        
        result = re.findall(re_str, script)
        phone = base64.b64decode(base64.b64decode(result[0])).decode("utf-8") 
        return phone




    def get_author(self, response):
        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = re.findall(re_str, script)
        return f'https://youla.ru/user/{result[0]}' if result else None


    def get_specifications(self, response):
        items = {}
        for item in response.css('.AdvertSpecs_row__ljPcX'):
            items[item.css('.AdvertSpecs_label__2JHnS::text').get()] = item.css('.AdvertSpecs_data__xK2Qx::text').get() or item.css('a::text').get()
        return items

