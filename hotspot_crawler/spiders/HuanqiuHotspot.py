#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/2 12:00
# @Author : chf2000
# @Contact : chenhongfan2000@hotmail.com
# @desc : 爬取环球网
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
import datetime
from ..items import HotspotCrawlerItem, HotspotCrawlerItemLoader
import datetime


# 调试输出
def debug_print(object):
    print()
    print("----------------------------DEBUG----------------------------")
    print("object:", object)
    print("----------------------------DEBUG----------------------------")
    print()


# 获取前1天或N天的日期，beforeOfDay=1：前1天；beforeOfDay=N：前N天
def get_date(before_of_day):
    today = datetime.datetime.now()
    # 计算偏移量
    offset = datetime.timedelta(days=-before_of_day)
    # 获取想要的日期的时间
    re_date = (today + offset).strftime('%Y-%m-%d')
    return re_date


class HuanqiuHotspotSpider(CrawlSpider):
    name = 'HuanqiuHotspot'
    allowed_domains = ['huanqiu.com', ]
    start_urls = ['http://www.huanqiu.com/', 'https://3w.huanqiu.com/']
    custom_settings = {
        'DEPTH_LIMIT': '3'
    }
    rules = (
        Rule(LinkExtractor(allow_domains=allowed_domains,
                           # allow=r"https?://[^\s]*\.huanqiu\.com/\S+/[^\s]*\.html",
                           #    restrict_xpaths=['//a[not(contains(@href,"agt=8"))]', '//a[not(@rel) or not(@class)]'],
                           deny=(r"http://\S+\.\S+\.com/\S+\?agt=8", r"/pic/", r"/photo/", r"/gallery/",
                                 r"weapon", r"humor")),
             callback='parse_item_huanqiu', follow=True),
    )

    def parse_item_huanqiu(self, response):
        print("parsing url %s" % response.url)
        item_loader = HotspotCrawlerItemLoader(item=HotspotCrawlerItem(), response=response)
        # url示例：https://3w.huanqiu.com/a/8b006e/7O2hOjqdbJm
        #          http://opinion.huanqiu.com/hqpl/2019-07/15093895.html
        try:
            item_loader.add_value("url", response.url)
            title = response.css('head>title::text').extract_first()
            title = re.sub(r"_\S+_\S+", repl="", string=title)
            title = re.sub(r"_\S+", repl="", string=title)
            item_loader.add_value("title", title.strip())
            publish_time = response.css('p.time::text').extract_first() or ""
            sql_publish_time = publish_time + ":00"

            # debug_print(sql_publish_time)
            publish_date = sql_publish_time.split(" ")
            publish_date = publish_date[0]

            # 生成的采集日期列表
            date_list = []
            # 采集的天数
            look_back_days = 14
            for i in range(0, look_back_days):
                date_list.append(get_date(i))
            item_loader.add_value("publish_time", sql_publish_time)
            if publish_date not in date_list:
                yield item_loader.load_item()
                return
            # else:
            #     debug_print("in the list")
            content_list = response.css('article>section>p::text').extract()
            content = '\n'.join(content_list)
            content = self.remove_spaces_and_comments(content)
            item_loader.add_value("content", content or "")
            yield item_loader.load_item()
        except Exception as e:
            self.logger.critical(msg=e)
            return None

    def remove_spaces_and_comments(self, repl_text):
        import re
        repl_text = re.sub(r'\s+', repl="", string=repl_text)
        repl_text = re.sub(r'\u3000', repl="", string=repl_text)
        return re.sub(r'<!--\S+-->', repl="", string=repl_text)
