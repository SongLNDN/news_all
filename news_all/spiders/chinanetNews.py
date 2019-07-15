#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午4:38
 
 Function: 中国网爬虫
 
"""

import random
import re

import scrapy
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class bjNews(scrapy.Spider):
    name = "chinanetNewsSpider"
    start_url = "http://www.china.com.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://news.china.com.cn/node_7247300.htm", callback=self.parse_item_home,
                             headers=self.header)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""/html/body/div/div/ul/li/a/@href""").extract()
        for detail_url in detail_urls:
            time.sleep(random.uniform(1, 3))
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                # content_time = response.xpath("""//*[@id="pubtime_baidu"]/text()""").extract()
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)

            except:
                spiderUtil.log_level(8, response.url)

            try:
                contents = response.xpath("""//*[@id="articleBody"]/p/text()""").extract()
                content = "".join(contents)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.china.com.cn/"

            try:
                author_arr = response.xpath("""//*[@id="source_baidu"]//text()""").extract()
                author = "".join(author_arr)
                if author == '':
                    author = "中国网"
                else:
                    author = author.split("来源：")[1].strip()
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title_arr = response.xpath("/html/body/div/h1/text()").extract()
                title = "".join(title_arr).strip()
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
                    # print(item)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)
