#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc :
# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
from scrapy.exporters import JsonItemExporter

from hotspot_crawler.spiders.dbManager import MysqlOperation


class JSONWithEncodingPipeline(object):
    def __init__(self):
        super().__init__()
        # 输入爬取数据的json,测试用
        # today = datetime.datetime.now()
        # self.file = codecs.open(filename="./news_items/{}.json".format(int(today.timestamp())), mode="wb")
        # self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        # self.exporter.start_exporting()
        # 连接数据库
        self.db = MysqlOperation()

    def process_item(self, item, spider):
        # 生成hashcode作为标识
        hashcode = hashlib.md5(item["url"].encode(encoding='UTF-8')).hexdigest()
        # 向数据库插入爬取的数据
        if item["content"]:
            self.db.insert_data(item["url"], hashcode, item["title"], item["publish_time"], item["content"])
        # self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        # self.exporter.finish_exporting()
        # self.file.close()
        # 关闭数据库时断开连接
        self.db.dis_connect()


class ImageGettingPipeline(object):
    def process_item(self, item, spider):
        pass
