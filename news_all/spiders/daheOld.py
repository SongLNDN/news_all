# coding=utf-8
import scrapy
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class daheNews(scrapy.Spider):
    name = "daheSpider"
    start_url = "https://news.dahe.cn/"

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_item_home)

    def parse_item_home(self, response):
        list_news_arr = response.xpath("//span[@class='more']/a/@href").extract()
        for list_news in list_news_arr:
            yield scrapy.Request(url=response.url + list_news, callback=self.parse_item_list_news)

    def parse_item_list_news(self, response):
        url_arr = response.xpath("//ul[@class='newsleftul']/li/a/@href").extract()
        if len(url_arr) > 50:
            url_arr = url_arr[:50]
            for url in url_arr:
                time.sleep(1)
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                public_time = response.xpath("//head/meta[@name='publishdate']/@content").extract()[0].replace("年",
                                                                                                               "-").replace(
                    "月", "-").replace("日", " ") + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='cl']")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                author = response.xpath("//head/meta[@name='source']/@content").extract()[0].split("-")[1]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("//head/meta[@itemprop='name']/@content").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

            source = "https://www.dahe.cn/"

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
