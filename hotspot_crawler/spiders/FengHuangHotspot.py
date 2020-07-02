#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc : 爬取凤凰网
import json
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
from ..items import HotspotCrawlerItem, HotspotCrawlerItemLoader


class FengHuangHotspotSpider(CrawlSpider):
    name = 'FengHuangHotspot'
    allowed_domains = ['ifeng.com']
    start_urls = ['http://news.ifeng.com/', ]

    rules = (
        Rule(LinkExtractor(allow=r"^https?://news\.ifeng\.com/c/\w+$", restrict_css=r".content-14uJp0dk"), follow=False,
             callback='parse_items_fenghuang'),
    )

    def parse_items_fenghuang(self, response):
        print("parsing url %s" % response.url)
        item_loader = HotspotCrawlerItemLoader(item=HotspotCrawlerItem(), response=response)
        try:
            item_loader.add_value("url", response.url)
            metadatas = self.get_metadatas(response)
            publish_time = response.css('meta[name="og:time "]::attr(content)').extract_first()
            if not publish_time:
                item_loader.add_value("publish_time", metadatas.get('publish_time').replace("-", "."))
            else:
                item_loader.add_value("publish_time", publish_time.replace("-", "."))
            item_loader.add_value("title", metadatas.get("title") or "")
            item_loader.add_value("content", metadatas.get("content") or "")
            yield item_loader.load_item()
        except Exception as e:
            self.logger.critical(msg=e)
            return None

    def get_metadatas(self, response):
        """
        通过head>script下存取的变量获取内容
        :param response: 原始页面
        :return: 获取的标题，时间， 内容
        """
        data_from = ""
        for each in response.css('head>script').extract():
            if "var allData" and "\"nav\"" in each:
                data_from = each
                break
        match = re.search(r"var\sadData\s=\s.+", data_from)
        if match:
            data_from = data_from[:match.start()]
            c = json.loads(data_from.lstrip("<script>").strip().lstrip("var allData = ").rstrip(";"), encoding='utf-8')
            base_data = c.get('docData')
            slide_data = c.get('slideData')
            if base_data or slide_data:
                content = ""
                publish_time = base_data.get('newsTime')
                title = base_data.get('title') or ""
                if "contentData" in base_data and base_data.get('contentData'):
                    for each in base_data['contentData']['contentList']:
                        if each.get('type') == 'text':
                            content = each['data'] or ""
                        else:
                            print(each.get('type'))
                    content = self.deal_with_content(content)
                else:
                    content_list = []
                    for each in slide_data:
                        if each.get('type') == 'pic':
                            content_list.append(each.get('description'))
                        else:
                            print(each.get('type'))
                    content_list = list(set(content_list))
                    content = '\n'.join(content_list) or ""
                return {
                    "title": title or "",
                    "publish_time": publish_time or "",
                    "content": content or ""
                }
        return {}

    def deal_with_content(self, repl_text):
        soup = BeautifulSoup(repl_text, "lxml")
        return '\n'.join(string for string in soup.stripped_strings) or ""
