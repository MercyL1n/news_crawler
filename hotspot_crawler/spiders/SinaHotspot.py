#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc : 爬取新浪新闻
import datetime
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import HotspotCrawlerItem, HotspotCrawlerItemLoader


def get_sql_datetime(raw_datetime):
    """
    将时间转为可输入数据库的格式
    :param raw_datetime: 原始时间戳
    :return: 处理后的时间戳
    """
    parts_of_datetime = raw_datetime.split(" ")
    pulish_time = parts_of_datetime[-1] + ":00"
    date = parts_of_datetime[0]
    date = date.replace('年', '.')
    date = date.replace('月', '.')
    date = date.replace('日', ' ')
    return date + pulish_time


class SinaHotspotSpider(CrawlSpider):
    name = 'SinaHotspot'
    allowed_domains = ['sina.com.cn', 'sina.com']
    start_urls = ['https://news.sina.com.cn/', ]
    reg = r"http(s)?://(\w+\.)?news.sina.com.cn/\w+/time/\w+-\w+\.(s)?html"
    # 爬取近两天的新闻
    t = time.localtime()
    now_time = time.strftime("%Y-%m-%d", t)
    reg = reg.replace("time", now_time)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_time = yesterday.strftime("%Y-%m-%d")
    reg2 = reg.replace("time", yesterday_time)
    rules = (
        Rule(LinkExtractor(
            allow=reg),
            callback='parse_sina_news', follow=True),
        Rule(LinkExtractor(
            allow=reg2),
            callback='parse_sina_news', follow=True),
    )

    def parse_sina_news(self, response):
        print("parsing url %s" % response.url)
        # start parsing
        item_loader = HotspotCrawlerItemLoader(item=HotspotCrawlerItem(), response=response)
        try:
            item_loader.add_value("url", response.url)
            item_loader.add_css("title", '.main-title::text') or ""
            publish_time = response.css('.date-source>span::text').extract_first()
            publish_time = get_sql_datetime(publish_time)
            item_loader.add_value("publish_time", publish_time) or ""
            content_list = response.css('.article>p::text').extract()
            content = self.remove_spaces_and_comments('\n'.join(content_list))
            item_loader.add_value("content", content)
            yield item_loader.load_item()
        except Exception as e:
            self.logger.critical(msg=e)
            return None

    def remove_spaces_and_comments(self, repl_text):
        import re
        repl_text = re.sub(r'\s+', repl="", string=repl_text)
        repl_text = re.sub(r'\u3000', repl="", string=repl_text)
        return re.sub(r'<!--\S+-->', repl="", string=repl_text)
