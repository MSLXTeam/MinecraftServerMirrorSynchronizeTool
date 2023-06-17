from download import download
import subprocess as sp
import os
import publib

spigot_version_list = ['1.20','1.19.4','1.19.3','1.19.2', '1.19.1', '1.19','1.18.2', '1.18.1', '1.18', '1.17.1', '1.17', '1.16.5', '1.16.4', '1.16.3', '1.16.2',
                '1.16.1', '1.16.', '1.15.2', '1.15.1', '1.15', '1.14.4', '1.14.3', '1.14.2', '1.14.1',
                '1.14', '1.13.2', '1.13.1', '1.13', '1.12.2', '1.12.1', '1.12', '1.11.2', '1.11.1',
                '1.11', '1.10.2', '1.10.1', '1.10', '1.9.4', '1.9.3', '1.9.2', '1.9.1', '1.9', '1.8.8',
                '1.8.7', '1.8.6', '1.8.5', '1.8.4', '1.8.3', '1.8.2', '1.8.1', '1.8']
supported_server = ['Paper&Folia','Mohist','Catserver']
mohist_versions = ['1.7.10','1.12.2','1.16.5','1.18.2','1.19.2','1.19.4','1.20']
paper_versions = ['1.8.8','1.9.4','1.10.2','1.11.2','1.12.2','1.13.2','1.14','1.15.2','1.16.5','1.17.1','1.18.2','1.19.4']
catserver_versions = ['1.12.2','1.16.5','1.18.2']

def test_server():
    for server in supported_server:
        if os.path.exists(server):
            print(f"已检测到{server}的仓库,正在尝试拉取")
            sp.run(['git','pull'],cwd=f'./{server}/')
        elif server == "Paper&Folia":
            print("正在尝试Clone Paper和Folia的仓库")
            '''Clone Paper&Folia仓库'''
            sp.run(['git','clone','https://github.com/PaperMC/Folia.git'])
            sp.run(['git','clone','https://github.com/PaperMC/Paper.git'])
        elif server == "Mohist":
            print("正在尝试Clone Mohist的仓库")
            for mo_ver in mohist_versions:
                sp.run(['git','clone','https://github.com/MohistMC/Mohist.git',f'Mohist-{mo_ver}','-b',mo_ver])
        elif server == "Catserver":
            print("正在尝试Clone Catserver的仓库")
            for ct_ver in catserver_versions:
                sp.run(['git','clone','https://github.com/engineer1109/CatServer-1.git',f'Catserver-{ct_ver}','-b',ct_ver])
        
    if not os.path.exists("BuildTools.jar"):
        print("未检测到BuildTools.jar,正在下载")
        '''下载BuildTools.jar(Spigot&Bukkit)'''
        download("https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar",down_name="BuildTools.jar")
    else:
        print("已存在BuildTools.jar,将不会再次进行下载")

'''编译Paper&Folia'''
def compile_paper():
    for pp_ver in paper_versions:
        print(f"开始编译Paper,版本:{pp_ver}")
        sp.run(['./gradlew applyPatches','./gradlew createReobfBundlerJar'],cwd='./Paper/')
    print("开始编译Folia,latest")
    sp.run(['./gradlew applyPatches','./gradlew createReobfBundlerJar'],cwd='./Folia/')

'''编译Spigot&CraftBukkit'''
def compile_spigot():
    for version in spigot_version_list:
        '''编译Spigot(以及1.14以下的CraftBukkit)'''
        sp.run(['java','-jar','BuildTools.jar',f'--rev={target-version}','--output-dir="./Spigot/"'])
        if eval(version) >= 1.14:
            '''编译CraftBukkit(1.14及以上)'''
            sp.run(['java','-jar','BuildTools.jar',f'--rev={target-version}','--output-dir="./Bukkit/"','--compile craftbukkit'])
        
'''编译Mohist'''
def compile_mohist():
    for mo_ver in mohist_versions:
        print(f"开始编译Mohist,版本:{mo_ver}")
        if mo_ver == '1.7.10':
            sp.run(['./gradlew setupCauldron launch4j'],cwd=f'./Mohist-{mo_ver}/')
        elif mo_ver == '1.12.2':
            sp.run(['./gradlew setup installerJar'],cwd=f'./Mohist-{mo_ver}/')
        else:
            sp.run(['./gradlew setup mohist.jar'],cwd=f'./Mohist-{mo_ver}/')
        
'''编译Catserver'''
def compile_catserver():
    for ct_ver in catserver_versions:
        print(f"开始编译Catserver,版本:{mo_ver}")
        sp.run(['./gradlew setup','./gradlew genPatches','./gradlew build'],cwd=f'./Catserver-{ct_ver}')
    
if __name__ == '__main__':
    log('正在检测是否已有服务端仓库')
    test_server()
    log('编译Paper&Folia')
    compile_paper()
    log('编译Spigot&CraftBukkit')
    compile_spigot()
    log('编译Mohist')
    compile_mohist()
    log('编译Catserver')
    compile_catserver()