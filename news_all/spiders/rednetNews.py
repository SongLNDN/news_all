#!/usr/bin/env python 
# encoding: utf-8 
"""
 Created by songyao@mail.ustc.edu.cn on 2019/1/21 上午9:01

 Function:  爬取http://www.rednet.cn/新闻数据
"""
import datetime
import random
import requests
import time
import socket
import re
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from lxml import etree
import logging
import os
import sys


import random
import scrapy
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class xuanjiangjiaNews(scrapy.Spider):
    name = "rednetNewsSpider"
    start_url = "http://www.rednet.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="https://jishou.rednet.cn/channel/7250.html", callback=self.parse_item_home,headers=self.header)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""//*[@id="div_newsList"]/ul/li/a/@href""").extract()
        for detail_url in detail_urls:
            time.sleep(random.uniform(1, 2))
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)


    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_time = response.xpath("//main/section/section/div/span[4]/text()").extract()
                public_time = str(str(content_time[0])+":00")

            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("/html/body/main/section/section/article/section/p/text()").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.rednet.cn/"

            try:
                author_arr = response.xpath("//main/section/section/div/span[1]/text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "红网"
                else:
                    author = author.split("来源：")[1]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title_arr = response.xpath("//main/section/section/h1/text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                # if content != "" and public_time.startswith(spiderUtil.get_first_hour()):
                    item = NewsAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = public_time
                    item["url"] = response.url
                    item["title"] = title
                    item["author"] = author
                    item["crawl_time"] = spiderUtil.get_time()
                    item["html_size"] = html_size
                    print(item)
                    # yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)















