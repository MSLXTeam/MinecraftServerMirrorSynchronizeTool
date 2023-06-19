# Introduction

此工具的设计,旨在使用命令行更方便地同步各个服务端的版本,适用于想要搭建服务端镜像站的用户

## 基础语法

* ``-S(--Synchronize)`` 从指定的服务器服务器同步Versions.json到本地(不会覆写本地文件)
* ``-L(--Local)`` 使用本地的Versions.json文件,一般用于增量下载
* ``-I(--Install)`` 从Versions.json里列出的下载链接下载对应的二进制包(*.jar)
* ``-C(--Compile)`` 从指定服务端的Github仓库下载源代码并编译
* ``-R(--Remove)`` 删除本地缓存
* ``-Q(--Query)`` 从指定的服务器查询和指定的名称和版本相匹配的项
* ``-y`` 更新本地的Versions.json文件(一般与 ``-S``配合使用)
* ``-m(--use-mirror)`` 使用指定的URl下载Versions.json文件
* ``-Remove-ALL`` 删除除了程序本身之外当前目录下的**所有文件**(包括Versions.json),是**最为激进**的删除缓存方案,**不推荐使用**
* 

# NGINX搭建文件下载服务

> 以下教程皆以Arch Linux为平台
>
> NGINX初学者文档(English):([Beginner’s Guide (nginx.org)](https://nginx.org/en/docs/beginners_guide.html))

希望不要滚挂

```bash
sudo pacman -Syyu
```

安装Nginx

```bash
sudo pacman -S nginx-mainline
```

> 如需稳定版本请去掉-mainline,nginx-mainline为主线版本,nginx为稳定版本

创建文件服务器的配置文件

首先在你的磁盘里选择一个风水宝地来当作存储文件的目录,然后创建一个配置文件（请根据实际情况更改配置）

```bash
mkdir ~/mcserversync/website/
touch /etc/nginx/conf.d/mcserversync.conf
```

再在你的磁盘里选择另一个风水宝地来当作存储访问日志的目录

```bash
touch ~/nginx_logs/mcsrvsync.log
```

然后在 ``mcserversync.conf``文件里输入以下内容（示例配置）:

```bash
vim /etc/nginx/conf.d/mcserversync.conf
```

```nginx
 server { 
        access_log ~/nginx_logs/mcsrvsync.log;#配置访问日志存放地址
        listen       19198;        #文件服务器端口根据实际配置
        charset utf-8;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;  
  
        location / {  
            root    ~/mcserversync/website/;#文件服务器中存放文件的目录, 请根据实际配置
        }   
}
```

快速查看nginx主配置文件的位置
``nginx -t``

在主配置文件的http代码块中增加以下内容(此处也请替换为你自己的文件路径)

```nginx
include /etc/nginx/conf.d/mcserversync.conf;
```

最后，重启Nginx应用新配置

```bash
nginx -s reload
```

现在在浏览器中访问```localhost:19198```应该就能看到文件列表了