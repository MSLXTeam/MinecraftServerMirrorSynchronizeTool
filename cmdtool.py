import argparse
import shutil
import downloadserver as DS
import compileserver as CS
from publib import *

parser = argparse.ArgumentParser(prog='Minecraft Server Mirror Synchronize Helper',usage='python3 -m cmdtool [Options]')
group_type = parser.add_mutually_exclusive_group()
group_file = parser.add_mutually_exclusive_group()

group_file.add_argument('-S','--Synchronize',help='Synchronize versions.json from the server',action='store_true')
group_file.add_argument('-L','--Local',help='Use local versions.json',default=None,nargs=1,type=str,metavar='path')
group_file.add_argument('-P','--Pull',help='Pull local git repo(Compile)',action='store_true')

parser.add_argument('-Q','--Query',help='Find all versions available on the specified server in the specified versions.json',nargs=1,type=str,metavar='ServerName')

group_type.add_argument('-I','--Install',help='Download the binary file of the target server(.jar)',nargs=2,default=None,metavar=('[Type of Server]','[Target version]'),type=str)
group_type.add_argument('-C','--Compile',help='Download the source code of the target server (if available) and compile it',type=str,nargs=2,default=None,metavar=('[Type of Server]','[Target version]'))
group_type.add_argument('-R','--Remove',help='Clean up files(Using it twice will erase all files except the program itself)',action='count')

parser.add_argument('-y',help='Update Local Database',action='store_true')
parser.add_argument('-m','--mirror',help='Download the versions.json file from the specified URL',nargs=1,type=str,metavar='URl')

args = parser.parse_args()

if args.Synchronize == True:
    if args.y == True:
        log("使用了-y选项,将会覆盖本地数据库")
    else:
        DS.USE_TEMP_VERSIONLIST = 1
    if args.mirror != None:
        DS.PATH_TO_VERSIONLIST = args.mirror
    log("正在同步versions.json")
    log(f"指定的链接:{DS.PATH_TO_VERSIONLIST}")
    try:
        DS.is_url()
    except RemoteDisconnected:
        log(f"远程主机连接错误,请一会之后再次尝试或检查您的网络状态",2)
        exit()
    else:
        log("versions.json同步完成")
        log(f"已同步的versions.json位置:{DS.PATH_TO_VERSIONLIST}")
        
if args.Local != None:
    log(f"正在使用本地文件:{args.Local[0]}")
    DS.PATH_TO_VERSIONLIST = args.Local[0]
        
if args.Install:
    servername = args.Install[0].lower()
    log(f"要下载的服务端种类:{servername}")
    serversion = args.Install[1]
    log(f"要下载的服务端版本:{serversion}")
    funcname = f'DS.get_server_{servername}()'
    log(f"要执行的函数:{funcname}")
    eval(funcname)