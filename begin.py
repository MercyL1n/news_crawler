#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 16:54
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc : 程序入口

from scrapy import cmdline
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from hotspot_crawler.spiders.dbManager import MysqlOperation

# 爬虫列表
crawl_list = {
    'http://news.ifeng.com/': 'FengHuangHotspot',
    'https://new.qq.com/': 'TencentHotspot',
    'http://news.sohu.com/': 'SohuHotspot',
    'https://news.sina.com.cn/': 'SinaHotspot',
    'http://www.xinhuanet.com/': 'XinhuaHotspot',
    'http://news.baidu.com/': 'BaiduHotspot',
}
#     'http://huanqiu.com': 'HuanqiuHotspot'
if __name__ == '__main__':
    # 获取数据库
    db = MysqlOperation()
    # 获取数据库中储存的网站列表
    website_list = db.get_website_list()
    # 断开数据库
    db.dis_connect()
    # scrapy 通过 CrawlerProcess 来同时运行多个爬虫
    process = CrawlerProcess(get_project_settings())
    # 将可以爬取的站点加入爬取列表
    for website in website_list:
        if website[1] in crawl_list.keys():
            process.crawl(crawl_list[website[1]])
            print(str(website[2]) + "加入爬取列表")
        else:
            print("暂不支持", end="")
            print(website[2] if website[2] is not None else website[1])
    print("-----------------start-------------------")
    # 开始爬取
    process.start()
# cmdline.execute("scrapy crawl HuanqiuHotspot".split())
