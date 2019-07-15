#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   qqNews.py
@time:  2019-07-11 9:31 
@function: qq新闻爬虫
"""
import json
import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class qqNews(scrapy.Spider):
    name = "qqNewsSpider"
    taglist = ['ent','sports','finance','tech','news','sports_nba','fashion']
    header = spiderUtil.header_util()

    def start_requests(self):
        for tag in self.taglist:
            url = 'https://pacaio.match.qq.com/openapi/json?key=' + tag + ':' + spiderUtil.get_time()[:-9].replace("-","") + '&num=50'
            yield scrapy.Request(url=url, callback=self.parsepage, headers=self.header)

    def parsepage(self,response):
        newsjson = json.loads(response.text)
        newslist = newsjson['data']
        for news in newslist:
            url = news['url']
            publice_time = news['publish_time']
            author = news['source']
            title = news['title']
            meta = {
                'title': title,
                'public_time': publice_time,
                'author': author
            }
            yield scrapy.Request(url, callback=self.parsebody, meta=meta)

    def parsebody(self,response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_arr = response.xpath("//div[@class='content-article']/p//text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "https://news.qq.com/"

            try:
                if content != "" and str(response.meta["public_time"]).startswith(spiderUtil.get_first_hour()):
                    item = NewsAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = response.meta["public_time"]
                    item["url"] = response.url
                    item["title"] = response.meta["title"]
                    item["author"] = response.meta["author"]
                    item["html_size"] = html_size
                    item["crawl_time"] = spiderUtil.get_time()
                    # print(item)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)