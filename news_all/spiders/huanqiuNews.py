#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   huanqiuNews.py
@time:  2019-07-09 9:01 
@function: 环球网新闻爬虫
"""
import time
import re
import scrapy
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil
import sys


class huanqiuNews(scrapy.Spider):
    name = "huanqiuSpider"
    start_url = ["http://world.huanqiu.com/article/?agt=15438",
                 "http://china.huanqiu.com/article/?agt=15438"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url=url, callback=self.parse_item_list_news, headers=self.header)

    def parse_item_list_news(self, response):
        detail_urls = response.xpath("""/html/body/div/div/div/ul/li/h5/em/a/@href""").extract()
        for detail_url in detail_urls:
            if "article" in detail_url:
                yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0) + ":00"
            except:
                # spiderUtil.log_level(8, response.url)
                pass
            try:
                content_arr = response.xpath("""/html/body/div/div/div/div/div/p/text()""").extract()
                content = "".join(content_arr).strip()
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                title_arr = response.xpath("/html/body/div/div/div/div/h1/text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("""/html/body/div/div/div/div/div/span/a/text()""").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "环球网"
            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.huanqiu.com/"

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
