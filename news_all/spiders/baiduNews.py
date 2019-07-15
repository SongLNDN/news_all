#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午2:34
 
 Function: 百度新闻爬虫
 
""" 
import random
import scrapy
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class bjNews(scrapy.Spider):
    name = "baiduNewsSpider"
    start_url = "http://news.baidu.com.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="https://news.baidu.com/guonei", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/guoji", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/mil", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/finance", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/ent", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/sports", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/internet", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/tech", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/game", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/lady", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/auto", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/auto", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="https://news.baidu.com/house", callback=self.parse_item_home,headers=self.header)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""//a/@href""").extract()
        for detail_url in detail_urls:
            if detail_url.startswith("http://baijiahao.baidu.com"):
                time.sleep(random.uniform(1, 2))
                yield scrapy.Request(url=detail_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_time = response.xpath("""//*[@id="article"]/div/div/div/span/text()""").extract()
                public_time = str(time.strftime('%Y', time.localtime(time.time()))) +"-"+ str(content_time[0]) + " " + str(content_time[1]) + ":00"
            except:
                # spiderUtil.log_level(8, response.url)
                pass
            try:
                content_arr = response.xpath("""//*[@id="article"]/div/p/span/text()""").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://news.baidu.com/"

            try:
                author_arr = response.xpath("""//*[@id="article"]/div/div/p/text()""").extract()
                author = "".join(author_arr)
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title_arr = response.xpath("""//*[@id="article"]/div/h2/text()""").extract()
                title = "".join(title_arr)
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

