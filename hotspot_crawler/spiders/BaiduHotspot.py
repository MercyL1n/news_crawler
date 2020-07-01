#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc : 爬取百度新闻
import re
import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import HotspotCrawlerItem, HotspotCrawlerItemLoader


def replace_spaces_and_comments(repl_text):
    import re
    repl_text = re.sub(r'\s+', repl="", string=repl_text)
    repl_text = re.sub(r'\u3000', repl="", string=repl_text)
    return re.sub(r'<!--\w+-->', repl="", string=repl_text)


class BaiduHotspotSpider(CrawlSpider):
    name = 'BaiduHotspot'
    allowed_domains = ['baijiahao.baidu.com', 'mbd.baidu.com']
    start_urls = ['http://news.baidu.com/', ]

    rules = (
        Rule(LinkExtractor(allow_domains=allowed_domains), callback='parse_item_baidu', follow=True),
    )

    def parse_item_baidu(self, response):
        """
        处理爬取页面内容
        :param response: 原始页面
        :return: 提取的Item
        """
        # 输出当前爬取的页面
        print("parsing url %s" % response.url)
        item_loader = HotspotCrawlerItemLoader(item=HotspotCrawlerItem(), response=response)
        try:
            item_loader.add_value("url", response.url)
            item_loader.add_css("title", 'head>title::text')
            time_str = response.css('div.author-txt > div>span::text').extract()
            today = datetime.datetime.now()
            time_str[0] = re.sub(r"发布时间[：:]", repl="", string=time_str[0])
            time_str[0] = str(today.year) + '-' + time_str[0]
            item_loader.add_value("publish_time", time_str[0]+" "+time_str[1]+":00")
            content_list = response.css('div.article-content > p::text').extract()
            if not content_list:
                content_list = response.css('div.article-content > p > span::text').extract()
            content = '\n'.join(content_list)
            content = replace_spaces_and_comments(content)
            item_loader.add_value("content", content)
            return item_loader.load_item()
        except Exception as e:
            self.logger.critical(msg=e)
            return None
