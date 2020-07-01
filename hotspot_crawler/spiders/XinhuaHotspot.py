#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc : 爬取新华网
import copy
import time
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import HotspotCrawlerItem, HotspotCrawlerItemLoader


class XinhuaHotspotSpider(CrawlSpider):
    name = 'XinhuaHotspot'
    allowed_domains = ['xinhuanet.com']
    start_urls = ['http://www.xinhuanet.com/', "https://www.xinhuanet.com/", ]

    now_yearmonth = time.strftime("%Y-%m", time.localtime())
    now_day = time.strftime("%d", time.localtime())
    reg = r"https?://www\.xinhuanet\.com/\w+/ym/day/c_\d+"
    reg = reg.replace("ym", now_yearmonth).replace("day", now_day)
    rules = (
        Rule(LinkExtractor(allow=reg, deny=(
            r"https?://www\.xinhuanet\.com/english/\S+",
            r"https?://www\.xinhuanet\.com/photo/\S+",
            r"https?://www\.xinhuanet\.com/video/\S+")),
             follow=True, callback='parse_items_xinhua'),
    )

    def parse_items_xinhua(self, response):
        print("parsing url %s" % response.url)
        global request_more
        if response.meta.get('item') is None:
            item_loader = HotspotCrawlerItemLoader(item=HotspotCrawlerItem(), response=response)
            request_more = True
        else:
            item_loader = response.meta['item']
            print(item_loader.get_collected_values)
            request_more = False
        try:
            import re
            if not item_loader.get_collected_values("title"):
                item_loader.add_css("title", ".share-title::text")
            publish_time = response.css('.h-time::text').extract_first()
            item_loader.add_value("publish_time", publish_time.replace("-", "."))
            item_loader.add_value("url", response.url)
            # item_loader.add_css("abstract", 'meta[name="description"]::attr(content)')
            content = response.css('#p-detail>p').extract() or response.css(
                '#content>p::text, #content>p>span::text').extract() or\
                response.css('.main-aticle>p::text').extract()

            item_loader.add_value("content", self.deal_with_content(''.join(content)))
            more_pages = response.css('#div_currpage>a::attr(href)').extract()
            if more_pages and not request_more:
                # 先去重
                temp = list(set(more_pages))
                temp.sort(key=more_pages.index)
                for url in temp:
                    print("more pages,continue parsing")
                    yield scrapy.Request(
                        url=url, callback=self.parse_items_xinhua,
                        meta=copy.deepcopy({'item': item_loader.load_item()})
                    )
            yield item_loader.load_item()
        except Exception as e:
            self.logger.critical(msg=e)
            return None

    def deal_with_content(self, repl_text):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(repl_text, "lxml")
        contents = soup.find_all('p')
        return ''.join(i.string for i in contents if i.string) or ""
