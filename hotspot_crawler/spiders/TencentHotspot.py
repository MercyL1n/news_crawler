#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc : 爬取腾讯新闻
import json
import re
from json import JSONDecodeError
import scrapy
from ..items import HotspotCrawlerItem


class TencentHotspotSpider(scrapy.Spider):
    name = "TencentHotspot"

    allowed_domains = ["qq.com"]
    allLink = [
        "https://pacaio.match.qq.com/irs/rcd?cid=137&token=d0f13d594edfc180f5bf6b845456f3ea&id=&ext=top&page=0&expIds"
        "=&callback=__jp1",
        "https://pacaio.match.qq.com/irs/rcd?cid=4&token=9513f1a78a663e1d25b46a826f248c3c&ext=&page=0&expIds"
        "=&callback=__jp2"]
    start_urls = [
        "https://pacaio.match.qq.com/irs/rcd?cid=137&token=d0f13d594edfc180f5bf6b845456f3ea&id=&ext=top&page=0&expIds"
        "=&callback=__jp1"]
    for i in range(0, 11):
        url = "https://pacaio.match.qq.com/irs/rcd?cid=137&token=d0f13d594edfc180f5bf6b845456f3ea&ext=top&page=" + str(
            i + 1) + "&callback=__jp" + str(i + 4)
        allLink.append(url)

    def parse(self, response):
        for link in self.allLink:
            yield scrapy.Request(url=link, callback=self.parse_top_news)

    def parse_top_news(self, response):
        origin = response.text
        trimmed = re.sub(pattern="__jp\\d+", repl="", string=origin).strip('()')
        try:
            articles = json.loads(trimmed, encoding='utf-8')
        except JSONDecodeError:
            try:
                if trimmed.endswith('])'):
                    articles = json.loads(trimmed[:-2], encoding='utf-8')
                elif trimmed.startswith('(['):
                    articles = json.loads(trimmed[1:], encoding='utf-8')
                else:
                    articles = trimmed
                    raise Exception("数据解析错误，跳过当前url", articles)
                    # 假如运行到这里，就是json解析出问题了，立刻抛出异常结束这个url的抓取
            except Exception as e:
                self.logger.critical(msg="遇到异常，调试信息如下：\n%s" % e.args)
                return
        if 'code' not in articles:
            # 是今日要闻
            for article in articles:
                news = HotspotCrawlerItem()
                news['title'] = article['title']
                # news['content_url'] = article['url']
                # news['newsId'] = article['article_id'].upper()
                # news['source'] = "腾讯新闻"
                yield scrapy.Request(url=article['url'], callback=self.parse_news_contents)
        else:
            # 是热点精选
            if articles['code'] == 0:
                articles = articles['data']
                for article in articles:
                    news = HotspotCrawlerItem()
                    news['title'] = article['title']
                    news['publish_time'] = article['publish_time']
                    yield scrapy.Request(url=article['vurl'], callback=self.parse_news_contents)
            else:
                self.logger.error(msg="处理请求出错，原因：返回值非零")
                return None

    def parse_news_contents(self, response):
        url = response.url
        print("parsing url %s" % url)
        if re.match(r"https://new.qq.com/\w+", string=url):
            if re.match(r"https?://new.qq.com/notfound.htm\w+", string=url):
                return None
            if re.match(r"https://new.qq.com/omn/\w+/\w+.html", string=url):
                news_id = url.split('/')[-1][:-5]
            elif re.match(r"https://new.qq.com/zt/template/\?id=\w+", string=url):
                news_id = url.split('/')[-1][4:]
            else:
                news_id = url.split('/')[-1]
            # print("current news id: %s" % news_id)
            yield scrapy.Request(
                url="https://openapi.inews.qq.com/getQQNewsNormalContent?id={}&refer=mobilewwwqqcom&otype=json&ext_data=all&srcfrom=newsapp&callback=getNewsContentOnlyOutput"
                    .format(news_id), callback=self.parse_news_api_json)
        else:
            # 不满足以上三条的链接应该不会是一条新闻了
            return None

    def parse_news_api_json(self, response):
        # print(response.url)
        content = json.loads(s=response.text, encoding="utf-8")
        # 当且仅当返回码为0的时候，才继续解析
        if content.get('ret') == 0:
            news = HotspotCrawlerItem()
            news['title'] = content.get('title')
            news['url'] = response.url
            news['publish_time'] = content.get('pubtime').replace("-", ".")
            content_news = content.get("ext_data").get("cnt_html")
            news['content'] = self.del_html_labels(content_news)
            return news
        else:
            self.logger.critical(msg="返回码为%d，api解析失败" % content.get('ret'))
            return None

    def del_html_labels(self, html_text):
        """
        删除提取内容中的html标签
        :param html_text: 提取的内容
        :return: 去除html标签后的内容
        """
        html_text = html_text.replace('\\', '')
        html_text = re.sub(r'<!--H2-->\S+<!--/H2-->', repl="", string=html_text)
        html_text = re.sub(r'\u3000', repl="", string=html_text)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_text, "lxml")
        return soup.text
