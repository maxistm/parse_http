import datetime as dt
import json
import scrapy
from ..items import InstaChain
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
    
    def __init__(self, login, enc_password, query, *args, **kwargs):
        self.query = query # ['maxisfx', 'senia_free']
        self.login = login
        self.enc_passwd = enc_password
        self.users = {}
        self.visited_users = []
        self.queue = []
        super().__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(InstagramChainSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider
    
    @staticmethod
    def find_chain(users, query, chain, startuser):
        for user, frends in users.items():
            if query in frends:
                chain.insert(0, user)
                if user == startuser:
                    return chain
                else:
                    return InstagramChainSpider.find_chain(users, user, chain, startuser)




    def start_while(self, response):
        while len(self.queue) > 0:
            if self.users[self.queue[0]] == []:
               
                yield response.follow(f'/{self.queue[0]}/', callback=self.user_page_parse)
                return None
            else:
                v = self.queue.pop(0)
                for friend in self.users[v]:
                    # если friend не посещался
                    if friend not in self.visited_users:
                        # добавляем его в очередь
                        self.queue.append(friend)
                        self.users[friend] = []
                        # помечаем вершину как посещенную
                        self.visited_users.append(friend)
                        
                        # если friend является пунктом назначения, мы победили
                        if friend == self.query[1]: 
                            chain = []
                            chain.append(self.query[1])
                            #path.append(friend)
                            self.find_chain(self.users, self.query[1], chain, self.query[0])
                            yield InstaChain(
                                chain = chain,
                                start_user = self.query[0],
                                end_user = self.query[1]
                            )
                            return None
        print('Not found') 


    
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
                self.queue=[]
                self.visited_users.append('0')
                self.users[self.query[0]] = []
                self.queue.append(self.query[0])

                self.visited_users.append(self.query[0])
                yield from self.start_while(response)
                
             
    def double_link(self, user):
        frends = []
        frends.append('0')
        for follow in user['follow']:
            if follow in user['followers']:
                frends.append(follow)
        return frends
    
            
        # при условии, что мы имеем дело со смежным списком
        # например, таким: adj = {A: [B,C], B:[D,F], ... }
    def closed(self, reason): 
        #resp = requests.post("http://localhost:6800/schedule.json", data={'project': "default", 'spider': self.name})
        yield scrapy.Request(self.start_urls[0], callback=self.parse)#, errback=self.handle_error)

    def handle_error(self, failure):
        self.log("Error Handle: %s" % failure.request)
        self.log("Sleeping 60 seconds")

    def spider_closed(self, spider):
        scrapy.Request(self.start_urls[0], callback=self.parse, errback=self.handle_error, dont_filter=True)#, errback=self.handle_error)
        #resp = requests.post("http://localhost:6800/schedule.json", data={'project': "default", 'spider': self.name})
      
    def check_finish(self, next_level, user):
        try:
            #count_all_folow = next_level[user]['count_follow']
            #count_all_folowers = next_level[user]['count_followers']
            if next_level[user]['next_follow_none']  == 1 and next_level[user]['next_followers_none'] == 1:
                #if count_all_folow == 0 and count_all_folowers == 0 :
                for key, value in next_level.items():
                    self.users[key] = self.double_link(value)
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def user_page_parse(self, response):
        try:
            user_data = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
            next_level = {}
            next_level[user_data['username']] = {
                'follow':[], 
                'followers':[], 
                'next_followers_none': 0,
                'next_follow_none': 0,
                }


            yield from self.get_api_follow_request(response, user_data, next_level, None )
            yield from self.get_api_followers_request(response, user_data, next_level, None)
            print('start')
        except Exception as e:
            print(e)

    def get_api_follow_request(self, response, user_data, next_level, variables=None):
        try:
            if not variables:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                }
                
            url = f'{self.api_url}?query_hash={self.query_hash["follow"]}&variables={json.dumps(variables)}'
            yield response.follow(url, callback=self.get_api_follow, cb_kwargs={'user_data': user_data, 'next_level':next_level})
        except Exception as e:
            print(e)

    def get_api_follow(self, response, user_data, next_level):
        try:
            if b'application/json' in response.headers['Content-Type']:
                data = response.json()       
                if data['data']['user']['edge_follow']['page_info']['has_next_page'] == False:
                    next_level[user_data['username']]['next_follow_none'] = 1
                yield from self.get_follow_item(user_data, data['data']['user']['edge_follow']['edges'], response, next_level)

                if data['data']['user']['edge_follow']['page_info']['has_next_page']:
                    variables = {
                        'id': user_data['id'],
                        'first': 100,
                        'after': data['data']['user']['edge_follow']['page_info']['end_cursor'],
                    }
                    yield from self.get_api_follow_request(response, user_data, next_level, variables)
                    
                
        except Exception as e:
            print(e)

    def get_follow_item(self, user_data, follow_users_data, response, next_level):
        for user in follow_users_data:
            next_level[user_data['username']]['follow'].append(user['node']['username'])
        
        if self.check_finish(next_level,user_data['username']):
            yield from self.start_while(response)
            print(user_data['username'] + ' is_over')
         
        #print(user_data['username']  +  ' : ' + str(self.next_level[user_data['username']]))


    def get_api_followers_request(self, response, user_data, next_level, variables=None):
        try:
            if not variables:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                }
                
            url = f'{self.api_url}?query_hash={self.query_hash["followers"]}&variables={json.dumps(variables)}'
            
            yield response.follow(url, callback=self.get_api_followers, cb_kwargs={'user_data': user_data, 'next_level':next_level})
        except Exception as e:
            print(e)

    def get_api_followers(self, response, user_data, next_level):
        try:
            if b'application/json' in response.headers['Content-Type']:
                data = response.json()
                if data['data']['user']['edge_followed_by']['page_info']['has_next_page'] == False:
                    next_level[user_data['username']]['next_followers_none'] = 1
                yield from self.get_followers_item(user_data, data['data']['user']['edge_followed_by']['edges'], response, next_level)
                
                if data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
                    variables = {
                        'id': user_data['id'],
                        'first': 100,
                        'after': data['data']['user']['edge_followed_by']['page_info']['end_cursor'],
                    }
                    yield from self.get_api_followers_request(response, user_data, next_level, variables )
      
        except Exception as e:
            print(e)

    def get_followers_item(self, user_data, followers_users_data, response, next_level):
        for user in followers_users_data:
            next_level[user_data['username']]['followers'].append(user['node']['username'])
        
        if self.check_finish(next_level, user_data['username']):
            yield from self.start_while(response)
            print(user_data['username'] + ' is_over')
        #print(user_data['username']  +  ' : ' + str(self.next_level[user_data['username']]))


    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])
