#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   chinaNews.py
@time:  2019-07-08 17:13 
@function: 中国新闻网新闻爬虫
"""
import time
import re
import scrapy
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil
import sys


class chinaNews(scrapy.Spider):
    name = "chinaSpider"
    start_url = "http://www.chinanews.com/scroll-news/news1.html"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_item_list_news,headers=self.header)

    def parse_item_list_news(self, response):
        detail_urls = response.xpath("""//*[@id="content_right"]/div/ul/li/div/a/@href""").extract()
        for detail_url in detail_urls:
            if len(detail_url) > 40:
                # time.sleep(3)
                url = "http:" + str(detail_url)
                yield scrapy.Request(url=url, callback=self.parse,headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                public_time = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日\s\d{1,2}:\d{1,2})", response.text).group(0).replace("年", "-").replace("月", "-").replace("日", "") + ":00"
            except:
                # spiderUtil.log_level(8, response.url)
                pass
            try:
                content_arr = response.xpath("//div[@class='left_zw']/p//text()").extract()
                content = "".join(content_arr).strip()
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                title_arr = response.xpath("//div/div/div/div/h1//text()").extract()
                title = "".join(title_arr)
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//div[@class='left-t']//text()").extract()
                author = "".join(author_arr)
                if author == "":
                    author = "中国新闻网"
            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.chinanews.com/"

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
                    # print(item)
                    yield item
            except:
                pass

        else:
            spiderUtil.log_level(response.status, response.url)