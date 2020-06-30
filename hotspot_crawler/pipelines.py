# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import datetime
import hashlib
import traceback

import pymysql
from scrapy.exporters import JsonItemExporter

from hotspot_crawler.spiders.dbmanager import MysqlOperation


class JSONWithEncodingPipeline(object):
    def __init__(self):
        super().__init__()
        self.connect = pymysql.connect(
            # localhost连接的是本地数据库
            host='localhost',
            # mysql数据库的端口号
            port=3306,
            # 数据库的用户名
            user='root',
            # 本地数据库密码
            passwd='20200406',
            # 数据库名
            db='covid_db',
            # 编码格式
            charset='utf8'
        )
        # 2. 创建一个游标cursor, 是用来操作表。
        self.cursor = self.connect.cursor()
        today = datetime.datetime.now()
        self.file = codecs.open(filename="./news_items/{}.json".format(int(today.timestamp())), mode="wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()
        self.db = MysqlOperation()

    def process_item(self, item, spider):
        hashcode = hashlib.md5(item["url"].encode(encoding='UTF-8')).hexdigest()
        self.db.insert_data(item["url"], hashcode, item["title"], item["publish_time"], item["content"])
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
        MysqlOperation.dis_connect()


class ImageGettingPipeline(object):
    def process_item(self, item, spider):
        pass
