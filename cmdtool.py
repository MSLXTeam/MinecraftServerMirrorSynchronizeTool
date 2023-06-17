import argparse
import shutil
import downloadserver as DS
import compileserver as CS
parser = argparse.ArgumentParser(prog='Minecraft Server Mirror Synchronize Helper',usage='%(prog)s [Synchronize] [Update Local Database] [DownloadType] [Other Options]')
group_type = parser.add_mutually_exclusive_group(required=True)
parser.add_argument('-S','--Synchronize',help='Synchronize the list of available servers from the server')
parser.add_argument('-y',help='Update Local Database')
parser.add_argument('-m','--mirror',help='Download the versions.json file from the specified URL',nargs=1,type='str')
parser.add_argument('-Q','--Query',help='Find all versions available on the specified server in the specified Versions.json',nargs=1,type='str')
group_type.add_argument('-I','--Install',help='Download the binary file of the target server(.jar)',nargs=2,default=['Spigot','latest'],metavar=['Type of Server','Target Server version'],type='str')
group_type.add_argument('-C','--Compile',help='Download the source code of the target server (if available) and compile it',nargs=2,default=['Spigot','latest'],metavar=['Type of Server','Target Server version'],type='str')
group_type.add_argument('-R','--Remove',help='Clean up compiled build files (will be deleted along with compiled binaries!)',nargs=2,metavar=['Type of Server','Target Server version'])
group_type.add_argument('--RemoveALL',help='THIS COMMAND WILL REMOVE ALL FILES IN THE DIRECTORY EXCEPT THE PROGRAM BODY',nargs=2,metavar=['Type of Server','Target Server version'])
parser.parse_args()