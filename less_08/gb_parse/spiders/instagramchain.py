import datetime as dt
import json
import scrapy
from ..items import InstaUser, InstaFollow, InstaFollower
import requests

class InstagramChainSpider(scrapy.Spider):
    name = 'InstagramChain'
    db_type = 'MONGO'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    api_url = '/graphql/query/'
    query_hash = {
        'follow': 'd04b0a864b4b54837c0d870b0e77e076',
        'followers': 'c76146de99bb02f6415203be841dd25a'
    }
    visited_users = []

    def __init__(self, login, enc_password, next_level, users, *args, **kwargs):
        self.tags = ['python', 'программирование', 'developers']
        self.users = users # ['maxisfx', 'senia_free']
        self.login = login
        self.enc_passwd = enc_password
        self.next_level = next_level
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_passwd,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                for user in self.users:
                    yield response.follow(f'/{user}/', callback=self.user_page_parse)
                #self.bfs(self.users[0], self.users[1], response)
                
                #yield response.follow(f'/{self.users[0]}/', callback=self.user_page_parse, cb_kwargs={'find_user': self.users[0]})

        # при условии, что мы имеем дело со смежным списком
        # например, таким: adj = {A: [B,C], B:[D,F], ... }

    def spider_closed(self, spider):
        resp = requests.post("http://localhost:6800/schedule.json", data={'project': "default", 'spider': self.name})
      

    def user_page_parse(self, response):
        user_data = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        self.next_level[user_data['username']] = {'follow':[], 'followers':[]}
        #yield InstaUser(
        #     _id = user_data['id'],
        #     date_parse=dt.datetime.utcnow(),
        #     data=user_data
        #)

        yield from self.get_api_follow_request(response, user_data)
        yield from self.get_api_followers_request(response, user_data)

    def get_api_follow_request(self, response, user_data, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100,
            }
        url = f'{self.api_url}?query_hash={self.query_hash["follow"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_follow, cb_kwargs={'user_data': user_data})

    def get_api_follow(self, response, user_data):
        if b'application/json' in response.headers['Content-Type']:
            data = response.json()
            yield self.get_follow_item(user_data, data['data']['user']['edge_follow']['edges'])
            if data['data']['user']['edge_follow']['page_info']['has_next_page']:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                    'after': data['data']['user']['edge_follow']['page_info']['end_cursor'],
                }
                yield from self.get_api_follow_request(response, user_data, variables)

    def get_follow_item(self, user_data, follow_users_data):
        for user in follow_users_data:
            self.next_level[user_data['username']]['follow'].append(user['node']['username'])
            #yield InstaFollow(
            #    user_id=user_data['id'],
            #    user_name=user_data['username'],
            #    follow_id=user['node']['id'],
            #    follow_name=user['node']['username']
            #)
            #yield InstaUser(
            #    _id = user['node']['id'],
            #    date_parse=dt.datetime.utcnow(),
            #    data=user['node']
            #)
        print(self.next_level[user_data['username']])


    def get_api_followers_request(self, response, user_data, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100,
            }
        url = f'{self.api_url}?query_hash={self.query_hash["followers"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_followers, cb_kwargs={'user_data': user_data})

    def get_api_followers(self, response, user_data):
        if b'application/json' in response.headers['Content-Type']:
            data = response.json()
            yield self.get_followers_item(user_data, data['data']['user']['edge_followed_by']['edges'])
            if data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                    'after': data['data']['user']['edge_followed_by']['page_info']['end_cursor'],
                }
                yield from self.get_api_followers_request(response, user_data, variables)

    def get_followers_item(self, user_data, followers_users_data):
        for user in followers_users_data:
            self.next_level[user_data['username']]['followers'].append(user['node']['username'])
            """
            yield InstaFollower(
                user_id=user_data['id'],
                user_name=user_data['username'],
                follower_id=user['node']['id'],
                follower_name=user['node']['username']
            )
            yield InstaUser(
                _id = user['node']['id'],
                date_parse=dt.datetime.utcnow(),
                data=user['node']
            )
            """
        print(self.next_level[user_data['username']])


    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])
