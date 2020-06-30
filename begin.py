from scrapy import cmdline
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from hotspot_crawler.spiders.dbmanager import MysqlOperation
crawl_list = {
    'http://news.ifeng.com/': 'FengHuangHotspot',
    'https://new.qq.com/': 'TencentHotspot',
    'http://news.sohu.com/': 'SohuHotspot',
    'https://news.sina.com.cn/': 'SinaHotspot',
    'http://www.xinhuanet.com/': 'XinhuaHotspot',
    'http://news.baidu.com/': 'BaiduHotspot',
}
# 'huanqiu.com': 'HuanqiuHotspot'
db = MysqlOperation()

if __name__ == '__main__':
    website_list = db.get_website_list()
    db.dis_connect()
    process = CrawlerProcess(get_project_settings())
    for website in website_list:
        if website[1] in crawl_list.keys():
            process.crawl(crawl_list[website[1]])
            print(website[2]+"加入爬取列表")
        else:
            print("暂不支持"+website[2])
    print("-----------------start-------------------")
    process.start()
# cmdline.execute("scrapy crawl HuanqiuHotspot".split())