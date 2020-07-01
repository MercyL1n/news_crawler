#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc : 爬取搜狐
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import HotspotCrawlerItem, HotspotCrawlerItemLoader


class SohuHotspotSpider(CrawlSpider):
    name = 'SohuHotspot'
    allowed_domains = ['sohu.com']
    start_urls = ['http://news.sohu.com/', ]

    rules = (
        Rule(LinkExtractor(allow=r"^https?://www\.sohu\.com/a/\d{9,}_\d{6,}\S*$",
                           deny="picture/"), follow=False,
             callback='parse_items_sohu'),
    )

    def parse_items_sohu(self, response):
        import re
        print("parsing url %s" % response.url)
        item_loader = HotspotCrawlerItemLoader(item=HotspotCrawlerItem(), response=response)
        try:
            item_loader.add_value("url", response.url)
            title = response.css('head>title::text').extract_first()
            title = re.sub(r"_\S+", "", title)
            item_loader.add_value("title", title)
            publish_time = response.css('meta[itemprop="datePublished"]::attr(content)').extract_first()
            item_loader.add_value("publish_time", publish_time.replace("-", ".")+":00")
            cnt_list = response.css('article>p::text').extract()
            content = '\n'.join(i.strip() for i in cnt_list)
            content = self.remove_spaces_and_comments(content.strip("责任编辑："))
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
