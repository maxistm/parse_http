import re
import scrapy
from ..loaders import HhunterVacancyLoader, HhunterCompanyLoader
import requests
import json


class HhunterSpider(scrapy.Spider):
    name = 'hunter'
    db_type = 'MONGO'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/?customDomain=1']
    params = 'search/vacancy?schedule=remote&L_profession_id=0&area=113'

    css_query = {
        'vacancies': 'div.vacancy-serp div.vacancy-serp-item a.HH-VacancySidebarTrigger-Link',
    }

    xpath_query = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
    }

    itm_template = {
        'title': '//div[@class="vacancy-title"]/h1/text()',
        'salary': '//p[@class="vacancy-salary"]//text()',
        # 'description': '//div[@class="vacancy-description"]/div[@class="bloko-gap bloko-gap_bottom"]//text()',
        'description': 'concat(//div[@class="vacancy-description"]/div[@class="bloko-gap bloko-gap_bottom"]//text(), "\n", //div[@class="g-user-content"]//text())',
        'skills': '//div[@class="bloko-tag-list"]//text()',
        "company_url": '//a[@data-qa="vacancy-company-name"]/@href'
    }

    company_template = {
        'title': '//div[@class="company-header-title-name"]//text()',
        'description': '//div[@class="company-description"]/div[@class="g-user-content"]//text()',
    }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def parse(self, response):
        yield response.follow('search/vacancy?schedule=remote&L_profession_id=0&area=113', callback=self.vacancies_page_parse)

    def vacancies_page_parse(self, response):
        for pag_page in response.xpath(self.xpath_query['pagination']):
            yield response.follow(pag_page, callback=self.vacancies_page_parse)

        for vacancy in response.css(self.css_query['vacancies']):
            yield response.follow(vacancy.attrib.get('href'), callback=self.vacancy_parse)

    def vacancy_parse(self, response):
        loader = HhunterVacancyLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.itm_template.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()
        yield response.follow(response.xpath(self.itm_template['company_url']).get(), callback=self.company_parse)

    def get_vacancies(self, response):
        try:
            id_emp = response.url.split('/')[-1]
            url_v = 'https://hh.ru/shards/employerview/vacancies?page=0&currentEmployerId=' + \
                id_emp + '&json=true&regionType=OTHER&disableBrowserCache=false'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
            }
            response = requests.get(url=url_v, headers=headers)

            if response.status_code != 200:
                # todo Создать класс исключение
                raise Exception
            dic_vacancies = response.json()
            return dic_vacancies
        except Exception:
            return []

    def company_parse(self, response):
        loader = HhunterCompanyLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_value('vacancies', self.get_vacancies(response))

        for name, selector in self.company_template.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()

        # перебрать вакансии не успел выдаются по запросу в jsonjson
        # hh.ru/shards/employerview/vacancies?page=0&profArea=6&currentEmployerId=3845543&json=true&regionType=OTHER&disableBrowserCache=true
