# coding=utf-8
import random

import scrapy
import re
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class bjNews(scrapy.Spider):
    name = "bjnewsSpider"
    start_url = "http://www.bjnews.com.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_item_home,headers=self.header)

    def parse_item_home(self, response):
        list_page_arr1 = response.xpath("//div[@class='nav']/a/@href").extract()
        list_page_arr2 = response.xpath("//div[@class='menu_drop_list']/a/@href").extract()
        for list_page in list_page_arr1:
            if not list_page.startswith("http") and list_page != "wevideo" and list_page != "video":
                yield scrapy.Request(url=response.url + list_page[1:], callback=self.parse_item_page_list)
        for list_page in list_page_arr2:
            yield scrapy.Request(url=response.url + list_page[1:], callback=self.parse_item_page_list)

    def parse_item_page_list(self, response):
        for page in range(1, 3):
            yield scrapy.Request(url=response.url + "?page=" + str(page), callback=self.parse_item_news_list)

    def parse_item_news_list(self, response):
        news_url_arr1 = response.xpath("//ul[@id='news_ul']/li/a/@href").extract()
        news_url_arr2 = response.xpath("//ul[@id='news_ul']/li/div/a/@href").extract()
        news_url_arr1.extend(news_url_arr2)
        for news_url in news_url_arr1:
            if news_url.startswith("http"):
                time.sleep(random.uniform(1, 2))
                yield scrapy.Request(url=news_url, callback=self.parse)
            else:
                news_url = "http://www.bjnews.com.cn" + news_url
                time.sleep(random.uniform(1, 2))
                yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='content']/p/text()").extract()
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.bjnews.com.cn/"

            try:
                author = response.xpath("//span[@class='author']/text()").extract()[0].strip()
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("//div[@class='title']/h1/text()").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

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
