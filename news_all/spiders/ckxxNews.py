#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午4:32
 
 Function: 参考消息
 
""" 

import random
import scrapy
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class bjNews(scrapy.Spider):
    name = "ckxxNewsSpider"
    start_url = "http://www.cankaoxiaoxi.com/"
    header = spiderUtil.header_util()
    def start_requests(self):
        yield scrapy.Request(url="http://china.cankaoxiaoxi.com/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://world.cankaoxiaoxi.com/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://mil.cankaoxiaoxi.com/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://finance.cankaoxiaoxi.com//", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://culture.cankaoxiaoxi.com/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://science.cankaoxiaoxi.com/", callback=self.parse_item_home,headers=self.header)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""//*[@id="allList"]/div/div/div/div/p/a/@href""").extract()
        for detail_url in detail_urls:
            time.sleep(random.uniform(1, 2))
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)


    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_time = response.xpath("""//*[@id="pubtime_baidu"]/text()""").extract()
                public_time = str(content_time[0])

            except:
                spiderUtil.log_level(8, response.url)

            try:
                contents = response.xpath("""//*[@id="allList"]/div/div/div/p/text()""").extract()
                content = "".join(contents)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.cankaoxiaoxi.com/"

            try:
                author = str(response.xpath("""//*[@id="source_baidu"]/text()""").extract()[0].strip()).replace("来源：", "")

            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("//div/div/h1/text()").extract()[0]
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
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)


