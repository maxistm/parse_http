from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import Settings
from gb_parse.spiders.instagramchain import InstagramChainSpider
import dotenv
import os
import scrapy.crawler as crawler

import twisted.internet
from twisted.internet import reactor
from twisted.internet import task
from crochet import setup
from scrapy.utils.log import configure_logging
from multiprocessing import Process, Queue


def double_link(user):
    frends = []
    for follow in user['follow']:
        if follow in user['followers']:
            frends.append(follow)
    return frends

def get_next_freinds(users, frends):
    
    
    next_level = {}
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramChainSpider, login=os.getenv('LOGIN'),
                    enc_password=os.getenv('PASSWORD'), next_level = next_level, users = frends )
    crawl_proc.start()
    crawl_proc = None

    for key, value in next_level.items():
        users[key] = double_link(value)
    

def f(q, frends):
    try:
        crawl_settings = Settings()
        crawl_settings.setmodule('gb_parse.settings')
        next_level = {}
        runner = CrawlerRunner(settings=crawl_settings)
        deferred = runner.crawl(InstagramChainSpider,  login=os.getenv('LOGIN'),
                enc_password=os.getenv('PASSWORD'), next_level = next_level, users = frends)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        q.put(next_level)
    except Exception as e:
        q.put(e)
 # the wrapper to make it run more times
def run_spider(users, frends):
    
    q = Queue()
    p = Process(target=f, args=(q,frends))
    p.start()
    next_level = q.get()
    p.join()
        #d.addBoth(lambda _: l.start(0, False))
    for key, value in next_level.items():
        users[key] = double_link(value)

    #l = task.LoopingCall(run_spider2)
    #l.start(0)

    #reactor.run()


def bfs(s, t):
    path = []
    # s - начальная вершина
    # t - пункт назначения
    users = {}
    # инициализируем очередь
    queue = []
    # добавляем s в очередь

    queue.append(s)
    # помечаем s как посещенную вершину во избежание повторного добавления в очередь
  
    visited_users.append(s)
    frends = []
    frends.append(s)
    run_spider(users, frends)
    #get_next_freinds(users, frends)

    while len(queue) > 0:
        # удаляем первый (верхний) элемент из очереди
        v = queue.pop() 
        path.append(v)
        for friend in users[v]:
            # если friend не посещался
            if friend not in visited_users:
                # добавляем его в очередь
                queue.append(friend)
                # помечаем вершину как посещенную
                visited_users.append(friend)
                
                # если friend является пунктом назначения, мы победили
                if friend == t: 
                    path.append(friend)
                    return True, path
        run_spider(users, users[v])
        #get_next_freinds(users, users[v])        

    # если t не обнаружено, значит пункта назначения достичь невозможно
    return False

# from gb_parse import settings
dotenv.load_dotenv()
visited_users = []
if __name__ == '__main__':
    configure_logging()
    result, quere = bfs('maxisfx', 'benechka07')
    print(quere)

