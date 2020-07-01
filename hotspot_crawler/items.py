#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc :
# Define here the models for your scraped items
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst


class HotspotCrawlerItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    @classmethod
    def remove_spaces_and_comments(cls, repl_text):
        """
        去除文本中的空格和符号
        :param repl_text: 待处理文本
        :return: 处理后的文本
        """
        repl_text = re.sub(r'\s+', repl="", string=repl_text)
        repl_text = re.sub(r'\u3000', repl="", string=repl_text)
        return re.sub(r'<!--\S+-->', repl="", string=repl_text)


class HotspotCrawlerItem(Item):
    # 新闻链接
    url = Field()
    # 新闻标题
    title = Field(input_processor=MapCompose(HotspotCrawlerItemLoader.remove_spaces_and_comments))
    # 发布日期
    publish_time = Field()
    # 新闻内容详情
    content = Field(serializer=str, input_processor=MapCompose(HotspotCrawlerItemLoader.remove_spaces_and_comments))