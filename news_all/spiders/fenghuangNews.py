#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   fenghuangNews.py
@time:  2019-07-11 10:18 
@function: 凤凰网新闻爬虫
"""
import json
import re

import scrapy
import sys

from lxml import etree

from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class fenghuangNews(scrapy.Spider):
    name = "fenghuangNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        url = "http://news.ifeng.com/"
        yield scrapy.Request(url=url, callback=self.parsepage, headers=self.header)

    def parsepage(self,response):
        newslist = response.xpath("//h2/a/@href").extract()
        for url in newslist:
            newsurl = "http://" + url
            yield scrapy.Request(newsurl, callback=self.parsebody)

    def parsebody(self,response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            all_arr = response.xpath("""//script//text()""").extract()
            data = "".join(all_arr).split("allData = ")[1].split("var adData")[0].strip()[:-1]
            data = json.loads(data)
            doc = data['docData']
            try:
                public_time = doc['newsTime']

            except:
                spiderUtil.log_level(8, response.url)

            try:
                content = doc['contentData']['contentList'][0]['data']
                content = "".join(etree.HTML(content).xpath("//p//text()")).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://news.ifeng.com/"

            try:
                author = doc['source']
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = doc['title']
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
                    item["html_size"] = html_size
                    item["crawl_time"] = spiderUtil.get_time()
                    # print(item)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)