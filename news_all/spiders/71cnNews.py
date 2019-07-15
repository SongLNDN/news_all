#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午4:08
 
 Function: 宣讲家网
 
""" 
import random
import scrapy
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class bjNews(scrapy.Spider):
    name = "71cnNewsSpider"
    start_url = "http://www.71.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.71.cn/acastudies/bjyw/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/economy/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/politics/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/culture/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/community/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/ecology/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/dangjian/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/law/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/keji/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/jiaoyu/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/nationaldefense/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/international/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/expcolumn/history/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.71.cn/acastudies/impremarks/", callback=self.parse_item_home,headers=self.header)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""/html/body/div/div/div/div/ul/li/div/a/@href""").extract()
        for detail_url in detail_urls:
            time.sleep(random.uniform(1, 2))
            yield scrapy.Request(url=detail_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_time = response.xpath("""//*[@id="main"]/div/div/div/div/div/span[1]/text()""").extract()
                public_time = str(str(content_time[0])+":00")

            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("""//*[@id="article-content"]/p/text()""").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.71.cn/"

            try:
                author_arr = response.xpath("""//*[@id="main"]/div/div/div/div/div/span[2]/text()""").extract()
                author = "".join(author_arr)
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("""//*[@id="main"]/div/div/div/div/h1/text()""").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                if content != "" and public_time.startswith(spiderUtil.get_first_hour()):
                # if content != "" :
                    item = NewsAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = public_time
                    item["url"] = response.url
                    item["title"] = title
                    item["author"] = author
                    item["crawl_time"] = spiderUtil.get_time()
                    item["html_size"] = html_size
                    print(content,public_time,title,author)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)

