#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   wangyiNews.py
@time:  2019-07-10 17:01 
@function: 网易新闻爬虫
"""
import re
import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class wangyiNews(scrapy.Spider):
    name = "wangyiNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://money.163.com/special/002526BH/rank.html", callback=self.parsepage, headers=self.header)

    def parsepage(self,response):
        newslist = response.xpath("//div/table/tr/td/a")
        for news in newslist:
            url = news.xpath("./@href").extract()[0]
            title = news.xpath("./text()").extract()[0].strip()
            yield scrapy.Request(url,callback=self.parsebody, meta={"title": title})

    def parsebody(self,response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='endText']/p/text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            try:
                author_arr = response.xpath("//a[@id='ne_article_source']//text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "网易新闻"
            except:
                spiderUtil.log_level(9, response.url)

            source = "https://news.163.com/"

            try:
                if content != "" and public_time.startswith(spiderUtil.get_first_hour()):
                    item = NewsAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = public_time
                    item["url"] = response.url
                    item["title"] = response.meta["title"]
                    item["author"] = author
                    item["html_size"] = html_size
                    item["crawl_time"] = spiderUtil.get_time()
                    # print(item)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)