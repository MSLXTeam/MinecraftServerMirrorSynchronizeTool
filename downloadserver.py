# encoding: utf-8
import glob
import json
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
import time
import os
import datetime
import requests
import re
import subprocess as sp
import random
from publib import *

#PATH_TO_VERSIONLIST = 'html/msl/CC/versions.json'
PATH_TO_VERSIONLIST = 'http://msl.waheal.top/msl/CC/versions.json'
USE_SELF_TIME = 1
USE_TEMP_VERSIONLIST = 0
#DOWNLOAD_ROOT = 'html/files/servers'
DOWNLOAD_ROOT = f'{os.getcwd()}{os.sep}Downloads'

if not os.path.exists(DOWNLOAD_ROOT):
    os.mkdir(DOWNLOAD_ROOT)

#判断PATH_TO_VERSIONLIST是不是URl,如果是,就下载到本地
def is_url():
    global PATH_TO_VERSIONLIST
    global USE_TEMP_VERSIONLIST
    try:
        result = urllib.parse.urlparse(PATH_TO_VERSIONLIST)
        check_result = all([result.scheme, result.netloc])
    except ValueError:
        check_result = False
    if USE_TEMP_VERSIONLIST == 0 and check_result == True:
        downctl(PATH_TO_VERSIONLIST,'versions.json')
        PATH_TO_VERSIONLIST = os.path.abspath('versions.json')
    elif USE_TEMP_VERSIONLIST == 1 and check_result == True:
        downctl(PATH_TO_VERSIONLIST,'temp_versions.json')
        PATH_TO_VERSIONLIST = os.path.abspath('temp_versions.json')
        
def remove_versionsfile():
    global PATH_TO_VERSIONLIST
    global USE_TEMP_VERSIONLIST
    if USE_TEMP_VERSIONLIST == 1:
        os.remove("temp_version.json")
    elif USE_TEMP_VERSIONLIST == 0:
        os.remove("version.json")

def version_compare(version):
    if version.startswith('*'):
        return 100, 100
    
    # 使用正则表达式从版本号中提取主要版本号
    match = re.search(r"(\d+(\.\d+)+)", version)
    if match:
        version = match.group(1)
    
    # 将版本号中的每个部分转换为整数，并进行比较
    version_parts = version.split('.')
    version_parts = [int(part) for part in version_parts]
    
    # 添加0，以便对不完整的版本号进行比较（如1.7）
    version_parts += [0] * (4 - len(version_parts))
    return tuple(version_parts)

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
                    if os.path.exists(download_path+os.sep+filename):
                        log(f"文件 {filename} 已存在,跳过下载",1)
                    else:
                        # 定义文件名和保存路径
                        _file_name=f'/{file_name}-{version}.jar'
                        _download_path = download_path+_file_name

                        # 下载文件
                        #urllib.request.urlretrieve(_download_link, _download_path)


                        # 设置请求头
                        headers = {
                            'User-Agent': random.choice(ua_list),  # 模拟浏览器
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
                
                    ordered_data[version] = ip_adress+os.sep+filename
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
            if os.path.exists(download_path+os.sep+filename):
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
            ordered_data[version] = ip_adress+os.sep+filename
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
            ordered_data[version] = ip_adress+os.sep+filename
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
        
def download_latest_build_forge(data_key):
    with open(PATH_TO_VERSIONLIST, 'r', encoding='utf-8') as file:
        data = json.load(file)
    _data = data[data_key]
    # 创建有序字典来存储版本号和下载链接，并按照自定义的比较函数进行排序
    #ordered_data = dict(sorted(_data.items(), key=lambda x: version_compare(x[0]), reverse=True))
    # Step 1: 获取所有支持的Minecraft版本
    minecraft_versions_url = "https://bmclapi2.bangbang93.com/forge/minecraft"
    response = requests.get(minecraft_versions_url)
    minecraft_versions = response.json()

    # Step 2: 解析所有支持的Minecraft版本
    for minecraft_version in minecraft_versions:
        # Step 3: 获取特定Minecraft版本下的所有Forge构建版本
        forge_versions_url = f"https://bmclapi2.bangbang93.com/forge/minecraft/{minecraft_version}"
        response = requests.get(forge_versions_url)
        forge_versions = response.json()

        # Step 4: 找到最新的Forge构建版本
        latest_forge_version = max(forge_versions, key=lambda x: x["build"])
        forge_build_version = latest_forge_version["version"]

        # Step 5: 拼接最新的Forge下载链接
        download_url = f"https://bmclapi2.bangbang93.com/forge/download?mcversion={minecraft_version}&version={forge_build_version}&category=installer&format=jar"

        # Step 6: 使用下载链接进行后续操作
        # 下载或处理Forge安装文件，根据你的需求进行相应的操作
        log('版本'+minecraft_version+'地址'+download_url)
        _data[minecraft_version] = download_url
        # 更新下载链接
        #_data.clear()
        _data.update(_data)
    ordered_data = dict(sorted(_data.items(), key=lambda x: version_compare(x[0]), reverse=True))
    data[data_key] = ordered_data  # 将修改后的数据存回原始数据字典中
    
    # 写入更新后的 JSON 文件
    with open(PATH_TO_VERSIONLIST, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def download_latest_build_fabric(data_key):
    with open(PATH_TO_VERSIONLIST, 'r', encoding='utf-8') as file:
        data = json.load(file)
    _data = data[data_key]
    # 创建有序字典来存储版本号和下载链接，并按照自定义的比较函数进行排序
    ordered_data = dict(sorted(_data.items(), key=lambda x: version_compare(x[0]), reverse=True))
    # Step 1: 获取所有支持的Minecraft版本
    # Step 1: 获取所有支持的Fabric版本
    fabric_versions_url = "https://meta.fabricmc.net/v2/versions/game"
    response = requests.get(fabric_versions_url)
    fabric_versions = response.json()

    # Step 2: 过滤掉预览版和快照版
    stable_fabric_versions = [v for v in fabric_versions if v["stable"]]

    # Step 3: 获取加载器的最新版本
    loader_versions_url = "https://meta.fabricmc.net/v2/versions/loader"
    response = requests.get(loader_versions_url)
    loader_versions = response.json()

    latest_loader_version = loader_versions[0]["version"]

    # Step 4: 获取安装器的最新版本
    installer_versions_url = "https://meta.fabricmc.net/v2/versions/installer"
    response = requests.get(installer_versions_url)
    installer_versions = response.json()

    latest_installer_version = installer_versions[0]["version"]

    for _minecraft_version in stable_fabric_versions:
        minecraft_version=_minecraft_version['version']
        # Step 5: 拼接下载链接
        download_url = f"https://meta.fabricmc.net/v2/versions/loader/{minecraft_version}/{latest_loader_version}/{latest_installer_version}/server/jar"

        # Step 6: 使用下载链接进行后续操作
        # 下载或处理Fabric安装文件，根据你的需求进行相应的操作
        log('版本'+minecraft_version+'地址'+download_url)
        ordered_data[minecraft_version] = download_url
        # 更新下载链接
        #_data.clear()
        _data.update(ordered_data)
    _ordered_data = dict(sorted(_data.items(), key=lambda x: version_compare(x[0]), reverse=True))
    data[data_key] = _ordered_data  # 将修改后的数据存回原始数据字典中
    
    # 写入更新后的 JSON 文件
    with open(PATH_TO_VERSIONLIST, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def download_latest_build_mohist(data_key, is_download=False, download_path='', ip_adress=''):
    with open(PATH_TO_VERSIONLIST, 'r', encoding='utf-8') as file:
        data = json.load(file)
    _data = data[data_key]
    # 获取可用的版本号列表
    versions_url = "https://mohistmc.com/api/versions"
    response = requests.get(versions_url)
    versions = response.json()

    # 遍历每个版本，获取构建 ID 和下载链接
    for version in versions:
        # 构建 API 请求 URL
        api_url = f"https://mohistmc.com/api/{version}/latest"
        response = requests.get(api_url)
        mdata = response.json()
    
        # 提取构建 ID 和下载链接
        build_id = mdata["number"]
        download_url = mdata["url"]
        filename=mdata["name"]

        log('版本'+version+'地址'+download_url)

        if is_download==True:
            # 检查文件是否已存在
            if os.path.exists(download_path+os.sep+filename):
                log(f"文件 {filename} 已存在，跳过下载")
            else:
                # 定义文件名和保存路径
                _download_path = download_path+"/"+filename
                # 下载构建文件

                # 下载文件
                #urllib.request.urlretrieve(_download_link, _download_path)


                # 设置请求头
                headers = {
                    'User-Agent': 'Mozilla/5.0',  # 模拟浏览器
                    'Referer': 'https://mohistmc.com/',  # 设置来源页面，有些服务器会进行检查
                    'Accept-Encoding': 'gzip, deflate',  # 接受的编码方式
                    'Connection': 'keep-alive',  # 保持连接
                }

                # 发送请求并获取响应
                response = requests.get(download_url, headers=headers)

                # 检查响应状态码
                if response.status_code == 200:
                    # 读取内容
                    html_content = response.content

                    # 保存文件
                    with open(_download_path, 'wb') as file:
                        file.write(html_content)
                    log(f"已下载 {filename} ")
                else:
                    log(f"Download failed with status code: {response.status_code}",2)

                #urllib.request.urlretrieve(download_url, _download_path)
                
            # 检查是否存在旧的构建文件
            pattern = re.compile(f"mohist-{re.escape(version)}-(.*)-server.jar")
            old_builds = glob.glob(os.path.join(download_path, "*.jar"))

            if len(old_builds) > 1:
                # 获取旧构建的版本和编号信息
                old_builds_info = [re.search(pattern, build).group(1) for build in old_builds if re.search(pattern, build)]
                for old_build in old_builds_info:
                    # 对比旧构建的版本和编号与最新构建是否一致
                    if int(old_build) != int(build_id):
                        # 删除旧构建文件
                        os.remove(os.path.join(download_path, f"mohist-{version}-{old_build}-server.jar"))
                        log(f"已删除旧构建文件 mohist-{version}-{old_build}-server.jar")
            '''
            # 检查是否存在旧的构建文件
            old_builds = glob.glob(download_path+"/"+f"mohist-{version}-*-server.jar")
            if len(old_builds) > 1:
                # 获取旧构建的版本和编号信息
                old_builds_info = [os.path.splitext(build)[0].split("-")[-2] for build in old_builds]
                for old_build in old_builds_info:
                    # 对比旧构建的版本和编号与最新构建是否一致
                    if int(old_build) != int(build_id):
                        # 删除旧构建文件
                        os.remove(download_path+"/"+f"mohist-{version}-{old_build}-server.jar")
                        print(f"已删除旧构建文件 mohist-{version}-{old_build}-server.jar")
            '''
            _data[version] = ip_adress+os.sep+filename
            # 更新下载链接
            #_data.clear()
            _data.update(_data)
        else:
            _data[version] = download_url
            # 更新下载链接
            #_data.clear()
            _data.update(_data)
    ordered_data = dict(sorted(_data.items(), key=lambda x: version_compare(x[0]), reverse=True))
    data[data_key] = ordered_data  # 将修改后的数据存回原始数据字典中
    
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
        log(f'执行函数{i + 1}:{func.__name__}')
        func()
        log('等待下一个函数执行...')

# 定义获取服务端地址的函数
def get_server_spigot():
    get_server_address('https://getbukkit.org/download/spigot', 'Spigot（插件服务端）',True,DOWNLOAD_ROOT,"spigot","http://47.243.96.125/files/servers/spigot")
    #get_server_address('https://getbukkit.org/download/spigot', 'Spigot（插件服务端）')

def get_server_vanilla():
    get_server_address('https://getbukkit.org/download/vanilla', 'Vanilla（原版服务端）')

def get_server_craftbukkit():
    get_server_address('https://getbukkit.org/download/craftbukkit', 'CraftBukkit（插件服务端）')

def get_server_paper():
    download_latest_builds('paper', 'Paper（插件服务端）',True,DOWNLOAD_ROOT,"http://47.243.96.125/files/servers/paper")
    #download_latest_builds('paper', 'Paper（插件服务端）')

def get_server_purpur():
    download_latest_builds_purpur('Purpur（插件服务端）',True,DOWNLOAD_ROOT,"http://47.243.96.125/files/servers/purpur")
    #download_latest_builds_purpur('Purpur（插件服务端）')

def get_server_folia():
    download_latest_builds('folia', 'Folia（多线程插件服务端）',True,DOWNLOAD_ROOT,"http://47.243.96.125/files/servers/folia")
    #download_latest_builds('folia', 'Folia（多线程插件服务端）')

def get_server_velocity():
    download_latest_builds('velocity', 'Velocity（代理服务端，单端勿用）',True,DOWNLOAD_ROOT,"http://47.243.96.125/files/servers/velocity")
    #download_latest_builds('velocity', 'Velocity（代理服务端，单端勿用）')

def get_server_forge():
    download_latest_build_forge('Forge（模组服务端，安装不稳定，建议使用二合一服务端）')

def get_server_fabric():
    download_latest_build_fabric('Fabric（模组服务端）')

def get_server_mohist():
    download_latest_build_mohist('Mohist（模组插件二合一服务端）',True,DOWNLOAD_ROOT,"http://47.243.96.125/files/servers/mohist")
    #download_latest_build_mohist('Mohist（模组插件二合一服务端）')

# Paper服务端示例
# project_id = "paper"
# download_latest_builds(project_id)

# Folia服务端示例
# project_id = "folia"
# download_latest_builds(project_id)


# 定义定时执行的函数列表
if __name__ == '__main__':
    functions = [get_server_purpur, get_server_folia, get_server_paper, get_server_spigot, get_server_vanilla, get_server_craftbukkit, get_server_velocity]

    try:
        is_url()
        execute_functions(functions)
    except ConnectionError:
        log('连接错误,请检查网络状态,程序即将退出',2)
        time.sleep(3)
        exit(1)
    except KeyboardInterrupt:
        log("已手动结束程序",1)
        exit()

    if USE_SELF_TIME == 0:
        # 输出现存的Crontab文件
        sp.run("crontab -l > newcron")
        sp.run("crontab -l > backupcron") #备份原来的Crontab文件以便恢复

        # 输出每日执行一次的指令到新的Crontab文件里
        with open('newcron', 'a') as f:
            f.write(f'0 0 * * * python3 {os.getcwd()}/{os.path.basename(__file__)}\n')

        # 安装新的Crontab文件
        sp.run('crontab newcron')

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