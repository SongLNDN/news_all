#!/usr/bin/env python
# coding: utf-8
"""
@author: TongYao
@file:   cqnNews.py
@time:  2019-07-09 11:01
@function: 文明网新闻爬虫
"""
import random
import re
import time

import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class cniiNews(scrapy.Spider):
    name = "cqnSpider"
    start_url = "http://www.cqn.com.cn/"

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_item_home)

    def parse_item_home(self, response):
        url_arr = response.xpath("//a/@href").extract()
        for url in url_arr:
            if url.endswith("htm"):
                if "content" in url:
                    yield scrapy.Request(url=response.url + url, callback=self.parse)
                elif "index" in url:
                    yield scrapy.Request(url=response.url + url, callback=self.parse_item_page)

    def parse_item_page(self, response):
        url_arr = response.xpath("//a/@href").extract()
        for url in url_arr:
            if url.endswith("htm"):
                if "content" in url:
                    yield scrapy.Request(url=response.url.split("index")[0] + url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                # spiderUtil.log_level(8, response.url)
                pass
            try:
                content_arr = response.xpath("//div[@class='content']//text()").extract()
                content = "".join(content_arr).strip()
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                title_arr = response.xpath("//head/title//text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//span[@class='from']//text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "中国质量新闻网"
            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.cqn.com.cn/"

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