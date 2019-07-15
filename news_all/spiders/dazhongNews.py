#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   dazhongNews.py
@time:  2019-07-09 8:22 
@function: 大众网新闻爬虫
"""
import time
import re
import scrapy
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil
import sys


class dazhongNews(scrapy.Spider):
    name = "dazhongSpider"
    start_url = ["http://www.dzwww.com/xinwen/guoneixinwen/",
                 "http://www.dzwww.com/xinwen/guojixinwen/",
                 "http://www.dzwww.com/xinwen/shehuixinwen/"]

    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url=url, callback=self.parse_item_list_news, headers=self.header)

    def parse_item_list_news(self, response):
        detail_urls = response.xpath("""//h3/a/@href""").extract()
        for detail_url in detail_urls:
            if detail_url.startswith("./"):
                url = response.url + detail_url.replace("./", "")
                yield scrapy.Request(url=url, callback=self.parse, headers=self.header)

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
                content_arr = response.xpath("""//div/div/div/div/div/p/text()""").extract()
                content = "".join(content_arr).strip()
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                title_arr = response.xpath("//div/div/h2/text()").extract()
                title = "".join(title_arr)
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("""//*[@id="xl-headline"]/div/div/text()""").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "大众网"
                else:
                    author = author.split("来源: ")[1].split("作者:")[0].strip()
            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.dzwww.com/"

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
