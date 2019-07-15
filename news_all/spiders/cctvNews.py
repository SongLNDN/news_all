#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   cctvNews.py
@time:  2019-07-09 10:34 
@function: CCTV网新闻爬虫
"""
import re
import time
import random
import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class cctvNews(scrapy.Spider):
    name = "cctvNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://news.cctv.com/?spm=C96370.PsikHJQ1ICOX.Eu7sfGTzJUS0.1",
                             callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""//a[starts-with(@href,'http://news.cctv.com/20')]/@href""").extract()
        for detail_url in detail_urls:
            if len(detail_url) < 70:
                time.sleep(random.uniform(1, 2))
                yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日\s\d{1,2}:\d{1,2})", response.text).group(0).replace("年","-").replace("月","-").replace("日","") + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("""/html/body/div/div/div/p/text()""").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.southcn.com/"

            try:
                author_arr = response.xpath("""/html/body/div/div/div/div/span/i/a/text()""").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "央视网"
                else:
                    author = author.replace("来源：", "")
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title_arr = response.xpath("""/html/body/div/div/div/h1/text()""").extract()
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
