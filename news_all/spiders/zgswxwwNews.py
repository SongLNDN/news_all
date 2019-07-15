#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午4:08
 
 Function: 中国商务新闻网
 
""" 
import random

import re
import scrapy
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class xuanjiangjiaNews(scrapy.Spider):
    name = "zgswxwwNewsSpider"
    start_url = "http://www.comnews.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.comnews.cn/article/pnews/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.comnews.cn/article/photo/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.comnews.cn/article/international/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.comnews.cn/article/local/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.comnews.cn/article/dzone/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.comnews.cn/article/abing/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.comnews.cn/article/ibdnews/", callback=self.parse_item_home,headers=self.header)
        yield scrapy.Request(url="http://www.comnews.cn/article/home/", callback=self.parse_item_home,headers=self.header)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""//ul[@class="col-ls alist"]//@href""").extract()
        for detail_url in detail_urls:
            # time.sleep(random.uniform(1, 2))
            detail_url = "http://www.comnews.cn" + detail_url
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)


    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_time = response.xpath("""//meta[@name="PubDate"]//@content""").extract()
                # print(content_time)
                # content_times = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", content_time[0]).group(0)
                # print(content_times)
                public_time =  str(content_time[0])

            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("""//div[@class="content"]//p//text()""").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.comnews.cn/"

            try:
                author = response.xpath("""//meta[@name="ContentSource"]//@content""").extract()[0].strip()
            except:
                spiderUtil.log_level(9, response.url)

            try:
                titles = response.xpath("""//meta[@name="ArticleTitle"]//@content""").extract()
                title = "".join(titles)
            except:
                spiderUtil.log_level(6, response.url)

            try:
                # if content != "" and str(public_time).startswith(spiderUtil.get_first_hour()):
                    item = NewsAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = public_time
                    item["url"] = response.url
                    item["title"] = title
                    item["author"] = author
                    item["crawl_time"] = spiderUtil.get_time()
                    item["html_size"] = html_size
                    print(item)
                    # yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)
