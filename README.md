# Introduction

此工具的设计,旨在使用命令行更方便地同步各个服务端的版本,适用于想要搭建服务端镜像站的用户

## 基础语法

* ```-S(--Synchronize)``` 从指定的服务器服务器同步Versions.json到本地(不会覆写本地文件)
* ```-L(--Local)``` 使用本地的Versions.json文件,一般用于增量下载
* ```-I(--Install)``` 从Versions.json里列出的下载链接下载对应的二进制包(*.jar)
* ```-C(--Compile)``` 从指定服务端的Github仓库下载源代码并编译
* ```-R(--Remove)``` 删除本地缓存
* ```-Q(--Query)``` 从指定的服务器查询和指定的名称和版本相匹配的项
* ```-y``` 更新本地的Versions.json文件(一般与```-S```配合使用)
* ```-m(--use-mirror)``` 使用指定的URl下载Versions.json文件
* ```-Remove-ALL``` 删除除了程序本身之外当前目录下的**所有文件**(包括Versions.json),是**最为激进**的删除缓存方案,**不推荐使用**
* 