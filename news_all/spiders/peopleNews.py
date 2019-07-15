#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   peopleNews.py
@time:  2019-07-09 10:44 
@function: 人民网新闻爬虫
"""
import json
import re
import time
import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class peopleNews(scrapy.Spider):
    name = "peopleNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        now = int(time.time())
        url = 'http://news.people.com.cn/210801/211150/index.js?_='+str(now)
        yield scrapy.Request(url,callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        newsjson = json.loads(response.text)
        newslist = newsjson['items']
        for news in newslist:
            post_title = news['title']
            post_url = str(news['url'])
            yield scrapy.Request(url=post_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日\d{1,2}:\d{1,2})", response.text).group(0).replace("年","-").replace("月","-").replace("日"," ") + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='rwb_zw']/p//text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.people.com.cn/"

            try:
                author_arr = response.xpath("//div[@class='box01']/div[@class='fl']/a//text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "人民网"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title_arr = response.xpath("//h1//text()").extract()
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