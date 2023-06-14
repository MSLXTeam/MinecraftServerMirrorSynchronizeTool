# encoding: utf-8
import glob
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
import time
import os
import urllib.request
import datetime
import requests
import re
import subprocess as sp
import datetime
import random

#PATH_TO_VERSIONLIST = 'html/msl/CC/versions.json'
PATH_TO_VERSIONLIST = 'http://msl.waheal.top/msl/CC/versions.json'
USE_SELF_TIME = 1
USE_TEMP_VERSIONLIST = 0
#DOWNLOAD_ROOT = 'html/files/servers'
DOWNLOAD_ROOT = f'{os.getcwd()}'

#判断PATH_TO_VERSIONLIST是不是URl,如果是,就下载到本地
def is_url():
    global PATH_TO_VERSIONLIST
    global USE_TEMP_VERSIONLIST
    try:
        result = urllib.parse.urlparse(PATH_TO_VERSIONLIST)
        check_result = all([result.scheme, result.netloc])
    except ValueError:
        check_result = False
    opener = urllib.request.build_opener()
    # 构建请求头列表每次随机选择一个
    ua_list = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'
            ]
    opener.addheaders = [('User-Agent', random.choice(ua_list))]
    urllib.request.install_opener(opener)
    if USE_TEMP_VERSIONLIST == 0 and check_result == True:
        urlretrieve(PATH_TO_VERSIONLIST, filename='versions.json')
        PATH_TO_VERSIONLIST = os.path.abspath('versions.json')
    elif USE_TEMP_VERSIONLIST == 1 and check_result == True:
        urlretrieve(PATH_TO_VERSIONLIST, filename='temp_versions.json')
        PATH_TO_VERSIONLIST = os.path.abspath('temp_versions.json')
        
def remove_versionsfile():
    global PATH_TO_VERSIONLIST
    global USE_TEMP_VERSIONLIST
    if USE_TEMP_VERSIONLIST == 1:
        os.remove("temp_version.json")
    elif USE_TEMP_VERSIONLIST == 0:
        os.remove("version.json")
    
def log(content:str,level:int = 0):
    level_list = ['Information','Warning','Error']
    time = datetime.datetime.now().strftime('[%H:%M:%S]')
    print(time+level_list[level]+':'+content)

def version_compare(version):
    if version.startswith('*'):
        return 100, 100;
    match = re.search(r"(.*?)(?=-)", version)
    if match:
        version = match.group(1)
    # 拆分版本号和小版本号(如果存在)
    parts = version.split('.')
    middle_version = parts[1] if len(parts) > 1 else '0'
    minor_version = parts[2] if len(parts) > 2 else '0'

    # 返回元组,按照 middle_version 和 minor_version 进行排序
    return int(middle_version), int(minor_version)

# 获取服务端地址的函数
def get_server_address(url, data_key, downloaded=False, download_path='', file_name='', ip_adress=''):
    with open(PATH_TO_VERSIONLIST, 'r', encoding='utf-8') as file:
        data = json.load(file)
    _data = data[data_key]
    # 创建有序字典来存储版本号和下载链接,并按照自定义的比较函数进行排序
    ordered_data = dict(sorted(_data.items(), key=lambda x: version_compare(x[0]), reverse=True))
    
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req)
        html_content = response.read()
        response.close()

        # 使用 Beautiful Soup 解析网页内容
        soup = BeautifulSoup(html_content, 'html.parser')

        # 找到所有的下载面板
        download_panes = soup.find_all('div', class_='download-pane')

        for pane in download_panes:
            # 提取版本号
            version_element = pane.find('div', class_='col-sm-3').find('h2')
            if version_element:
                version = version_element.text.strip()
            else:
                version = 'Unknown'

            # 提取下载链接
            download_link = pane.find('div', class_='col-sm-4').find('a', class_='btn-download')['href']
            
            try:
                req = Request(download_link, headers={'User-Agent': 'Mozilla/5.0'})
                response = urlopen(req)
                html_content = response.read()
                response.close()

                # 使用 Beautiful Soup 解析网页内容
                _soup = BeautifulSoup(html_content, 'html.parser')

                # 查找真正的下载链接
                _download_div = _soup.find('div', class_='well')
                _download_link = _download_div.find('h2').find('a')['href']
                filename = f"{file_name}-{version}.jar"
                log('版本'+version+'地址'+_download_link)

                if downloaded==True:
                    if os.path.exists(download_path+'/'+filename):
                        log(f"文件 {filename} 已存在,跳过下载",1)
                    else:
                        # 定义文件名和保存路径
                        _file_name=f'/{file_name}-{version}.jar'
                        _download_path = download_path+_file_name

                        # 下载文件
                        #urllib.request.urlretrieve(_download_link, _download_path)


                        # 设置请求头
                        headers = {
                            'User-Agent': 'Mozilla/5.0',  # 模拟浏览器(Mozilla5.0)
                            'Referer': 'https://getbukkit.org/',  # 设置来源页面,有些服务器会进行检查
                            'Accept-Encoding': 'gzip, deflate',  # 接受的编码方式
                            'Connection': 'keep-alive',  # 保持连接
                        }

                        # 发送请求并获取响应
                        response = requests.get(_download_link, headers=headers)

                        # 检查响应状态码
                        if response.status_code == 200:
                            # 读取内容
                            html_content = response.content

                            # 保存文件
                            with open(_download_path, 'wb') as file:
                                file.write(html_content)
                        else:
                            log("Download failed with status code: {response.status_code}",2)


                    log(f'已下载 {filename} ')
                
                    ordered_data[version] = ip_adress+'/'+filename
                    # 更新下载链接
                    #_data.clear()
                    _data.update(ordered_data)
                else:
                    ordered_data[version] = _download_link
                    # 更新下载链接
                    #_data.clear()
                    _data.update(ordered_data)

            except HTTPError as e:
                log(f"发生异常: {e}")

    except HTTPError as e:
        log(f"发生异常: {e}",2)

    data[data_key] = _data  # 将修改后的数据存回原始数据字典中
    # 写入更新后的 JSON 文件
    with open(PATH_TO_VERSIONLIST, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    log('服务端下载/更新完成')

def get_latest_build_url(project_id, version):
    # 获取指定版本的构建列表
    build_url = f"https://api.papermc.io/v2/projects/{project_id}/versions/{version}"
    response = requests.get(build_url)
    bdata = json.loads(response.text)
    builds = bdata["builds"]

    # 获取最新构建的编号
    latest_build = builds[-1]
    return latest_build

def download_latest_builds(project_id, data_key, is_download=False, download_path='', ip_adress=''):
    with open(PATH_TO_VERSIONLIST, 'r', encoding='utf-8') as file:
        data = json.load(file)
    _data = data[data_key]
    # 创建有序字典来存储版本号和下载链接,并按照自定义的比较函数进行排序
    ordered_data = dict(sorted(_data.items(), key=lambda x: version_compare(x[0]), reverse=True))

    # 获取版本列表
    version_url = f"https://api.papermc.io/v2/projects/{project_id}"
    response = requests.get(version_url)
    vdata = json.loads(response.text)
    versions = vdata["versions"]

    for version in versions:
        # 获取最新构建的编号
        latest_build = get_latest_build_url(project_id, version)

        # 构建文件的保存路径和文件名
        filename = f"{project_id}-{version}-{latest_build}.jar"
        download_url = f"https://api.papermc.io/v2/projects/{project_id}/versions/{version}/builds/{latest_build}/downloads/{project_id}-{version}-{latest_build}.jar"
        log('版本'+version+'地址'+download_url,level=0)

        if is_download==True:
            # 检查文件是否已存在
            if os.path.exists(download_path+'/'+filename):
                log(f"文件 {filename} 已存在,跳过下载",1)
            else:
                # 定义文件名和保存路径
                _file_name=f'/{project_id}-{version}-{latest_build}.jar'
                _download_path = download_path+_file_name
                # 下载构建文件
                urllib.request.urlretrieve(download_url, _download_path)
                log(f"已下载 {filename}")

            # 检查是否存在旧的构建文件
            old_builds = glob.glob(f"{project_id}-{version}-*.jar")
            if len(old_builds) > 1:
                # 获取旧构建的版本和编号信息
                old_builds_info = [os.path.splitext(build)[0].split("-")[-1] for build in old_builds]
                for old_build in old_builds_info:
                    # 对比旧构建的版本和编号与最新构建是否一致
                    if int(old_build) != int(latest_build):
                        # 删除旧构建文件
                        os.remove(f"{project_id}-{version}-{old_build}.jar")
                        log(f"已删除旧构建文件 {project_id}-{version}-{old_build}.jar")
            ordered_data[version] = ip_adress+'/'+filename
            # 更新下载链接
            #_data.clear()
            _data.update(ordered_data)
        else:
            ordered_data[version] = download_url
            # 更新下载链接
            #_data.clear()
            _data.update(ordered_data)
    data[data_key] = _data  # 将修改后的数据存回原始数据字典中
    # 写入更新后的 JSON 文件
    with open(PATH_TO_VERSIONLIST, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    log('服务端下载/更新完成')
        
def get_latest_build_url_purpur(version):
    # 获取指定版本的构建列表
    build_url = f"https://api.purpurmc.org/v2/purpur/{version}"
    response = requests.get(build_url)
    bdata = json.loads(response.text)
    builds = bdata["builds"]

    # 获取最新构建的编号
    latest_build = builds["latest"]
    return latest_build

def download_latest_builds_purpur(data_key, is_download=False, download_path='', ip_adress=''):
    with open(PATH_TO_VERSIONLIST, 'r', encoding='utf-8') as file:
        data = json.load(file)
    _data = data[data_key]
    # 创建有序字典来存储版本号和下载链接,并按照自定义的比较函数进行排序
    ordered_data = dict(sorted(_data.items(), key=lambda x: version_compare(x[0]), reverse=True))

    # 获取版本列表
    version_url = f"https://api.purpurmc.org/v2/purpur"
    response = requests.get(version_url)
    vdata = json.loads(response.text)
    versions = vdata["versions"]

    for version in versions:
        # 获取最新构建的编号
        latest_build = get_latest_build_url_purpur(version)

        # 构建文件的保存路径和文件名
        filename = f"purpur-{version}-{latest_build}.jar"
        download_url = f"https://api.purpurmc.org/v2/purpur/{version}/{latest_build}/download"
        log('版本'+version+'地址'+download_url)

        if is_download==True:
            # 检查文件是否已存在
            if os.path.exists(download_path+os.sep+filename):
                log(f"文件 {filename} 已存在,跳过下载",1)
            else:
                # 定义文件名和保存路径
                _file_name=f'{os.sep}purpur-{version}-{latest_build}.jar'
                _download_path = download_path+_file_name
                # 下载构建文件
                urllib.request.urlretrieve(download_url, _download_path)
                log(f"已下载 {filename}")

            # 检查是否存在旧的构建文件
            old_builds = glob.glob(f"purpur-{version}-*.jar")
            if len(old_builds) > 1:
                # 获取旧构建的版本和编号信息
                old_builds_info = [os.path.splitext(build)[0].split("-")[-1] for build in old_builds]
                for old_build in old_builds_info:
                    # 对比旧构建的版本和编号与最新构建是否一致
                    if int(old_build) != int(latest_build):
                        # 删除旧构建文件
                        os.remove(f"purpur-{version}-{old_build}.jar")
                        log(f"已删除旧构建文件 purpur-{version}-{old_build}.jar")
            ordered_data[version] = ip_adress+'/'+filename
            # 更新下载链接
            #_data.clear()
            _data.update(ordered_data)
        else:
            ordered_data[version] = download_url
            # 更新下载链接
            #_data.clear()
            _data.update(ordered_data)
    data[data_key] = _data  # 将修改后的数据存回原始数据字典中
    # 写入更新后的 JSON 文件
    with open(PATH_TO_VERSIONLIST, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    log('服务端下载/更新完成')
        


'''
# 定义主函数
def main():
    # 调用获取服务端地址的函数,并指定URL和数据键
    get_server_address('https://getbukkit.org/download/spigot', 'Spigot(插件服务端)')

# 调用主函数
main()
'''

# 定义总执行函数
def execute_functions(func_list):
    for i, func in enumerate(func_list):
        log(f'执行函数 {i + 1}:')
        func()
        log('等待下一个函数执行...')

# 定义获取服务端地址的函数
def get_server_address_spigot():
    get_server_address('https://getbukkit.org/download/spigot', 'Spigot（插件服务端）',True,f"{DOWNLOAD_ROOT}spigot","spigot","http://47.243.96.125/files/servers/spigot")

def get_server_address_vanilla():
    get_server_address('https://getbukkit.org/download/vanilla', 'Vanilla（原版服务端）')

def get_server_address_craftbukkit():
    get_server_address('https://getbukkit.org/download/craftbukkit', 'CraftBukkit（插件服务端）')

def get_server_address_paper():
    download_latest_builds('paper', 'Paper（插件服务端）',True,f"{DOWNLOAD_ROOT}paper","http://47.243.96.125/files/servers/paper")

def get_server_address_purpur():
    download_latest_builds_purpur('Purpur（插件服务端）',True,f"{DOWNLOAD_ROOT}{os.sep}purpur","http://47.243.96.125/files/servers/purpur")

def get_server_address_folia():
    download_latest_builds('folia', 'Folia（多线程插件服务端）',True,f"{DOWNLOAD_ROOT}folia","http://47.243.96.125/files/servers/folia")

def get_server_address_velocity():
    download_latest_builds('velocity', 'Velocity（代理服务端,单端勿用）',True,f"{DOWNLOAD_ROOT}velocity","http://47.243.96.125/files/servers/velocity")

# Paper服务端示例
# project_id = "paper"
# download_latest_builds(project_id)

# Folia服务端示例
# project_id = "folia"
# download_latest_builds(project_id)


# 定义定时执行的函数列表
functions = [get_server_address_purpur, get_server_address_folia, get_server_address_paper, get_server_address_spigot, get_server_address_vanilla, get_server_address_craftbukkit, get_server_address_velocity]

try:
    is_url()
    execute_functions(functions)
except ConnectionError:
    log('连接错误,请检查网络状态,程序即将退出',2)
    time.sleep(3)
    exit(1)

if USE_SELF_TIME == 0:
    # 输出现存的Crontab文件
    sp.run("crontab -l > newcron")
    sp.run("crontab -l > backupcron") #备份原来的Crontab文件以便恢复

    # 输出每日执行一次的指令到新的Crontab文件里
    with open('newcron', 'a') as f:
        f.write(f'0 0 * * * python3 {os.getcwd()}/{os.path.basename(__file__)}\n')

    # 安装新的Crontab文件
    sp.run('crontab mycron')

elif USE_SELF_TIME == 1:
    # 计算时间间隔（1天后）
    one_day = datetime.timedelta(days=1)
    next_execution_time = datetime.datetime.now() + one_day

    # 执行定时执行函数
    while True:
        current_time = datetime.datetime.now()
        if current_time >= next_execution_time:
            execute_functions(functions)
            next_execution_time = current_time + one_day
        else:
            time.sleep(60)  # 每分钟检查一次是否到达执行时间