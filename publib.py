import datetime
import requests
import download
import random
import urllib

ua_list = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'
            ]

USE_DOWN_ENGINE = 'py'

def log(content:str,level:int = 0):
    level_list = ['Information','Warning','Error']
    time = datetime.datetime.now().strftime('[%H:%M:%S]')
    print(time+level_list[level]+':'+content)

def downctl(url,name):
    if USE_DOWN_ENGINE == 'py':
        download.download(down_url=url,down_name=name)
    elif USE_DOWN_ENGINE == 'urllib':
        opener = urllib.request.build_opener()
        # 构建请求头列表每次随机选择一个
        opener.addheaders = [('User-Agent', random.choice(ua_list))]
        urllib.request.install_opener(opener)
        urlretrieve(url, filename=name)