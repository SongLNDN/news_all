#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   wenmingNews.py
@time:  2019-07-09 11:01 
@function: 文明网新闻爬虫
"""
import re
import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class wenmingNews(scrapy.Spider):
    name = "wenmingNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.wenming.cn/a/yw/", callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""/html/body/div/div/ul/li/div/a/@href""").extract()
        for detail_url in detail_urls:
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", response.text).group(0) + "00:00:00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='TRS_Editor']/div/p//text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.wenming.cn/"

            try:
                author_arr = response.xpath("//div[@class='box01']/div[@class='fl']/a//text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "文明网"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title_arr = response.xpath("//div[@id='title_tex']//text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                if content != "" and public_time.startswith(spiderUtil.get_yesterday_date()):
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