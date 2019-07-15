# coding=utf-8
import scrapy
import re
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class youthNews(scrapy.Spider):
    name = "youthSpider"
    url = ["http://news.youth.cn/", ]

    def start_requests(self):
        yield scrapy.Request(url=self.url[0], callback=self.parse_item_home)

    def parse_item_home(self, response):
        kinds_arr = response.xpath("//div[@class='nav']/ul/li/a/@href").extract()
        for kinds in kinds_arr:
            if len(kinds) < 10 and kinds != "rdzt/":
                kinds_url = response.url + kinds
                yield scrapy.Request(url=kinds_url, callback=self.parse_item_news_first)

    def parse_item_news_first(self, response):
        yield scrapy.Request(url=response.url + "index.htm", callback=self.parse_item_news_list)
        for page in range(1, 3):
            page_lsit_url = response.url + "index_" + str(page) + ".htm"
            yield scrapy.Request(url=page_lsit_url, callback=self.parse_item_news_list)

    def parse_item_news_list(self, response):
        news_arr = response.xpath("//ul[@class='tj3_1']/li/a/@href").extract()
        for news_url in news_arr:
            if news_url.startswith("./"):
                yield scrapy.Request(url=response.url[:25] + news_url[1:], callback=self.parse)
            elif news_url.startswith("//"):
                yield scrapy.Request(url="http:" + news_url, callback=self.parse)
            else:
                yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//div[@class='TRS_Editor']")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                author_arr = response.xpath("//meta[@name='author']/@content").extract()
                if author_arr == []:
                    author = "中国青年网"
                else:
                    author = author_arr[0]
            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.youth.cn/"

            try:
                title = "".join(response.xpath("//head/title/text()").extract()[0].split("_")[:-2]).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                if content != "" and public_time.startswith(spiderUtil.get_first_hour()):
                    item = NewsAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = public_time
                    item["url"] = response.url
                    item["title"] = title
                    item["author"] = author
                    item["crawl_time"] = spiderUtil.get_time()
                    item["html_size"] = html_size
                    # 数据打入piplines处理
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)

