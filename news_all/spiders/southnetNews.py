#!/usr/bin/env python
# encoding: utf-8


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午2:34

 Function: 南方网新闻爬虫

"""
import time
import random
import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class southnetNews(scrapy.Spider):
    name = "southnetNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="http://www.southcn.com/pc2018/yw/node_384370.htm", callback=self.parse_item_home, headers=self.header)   # 要闻新闻
        yield scrapy.Request(url="http://news.southcn.com/gd/", callback=self.parse_item_home, headers=self.header)  # 广东新闻
        yield scrapy.Request(url="http://news.southcn.com/china/default.htm", callback=self.parse_item_home, headers=self.header)  # 中国新闻
        yield scrapy.Request(url="http://news.southcn.com/international/default.htm", callback=self.parse_item_home, headers=self.header)  # 国际新闻
        yield scrapy.Request(url="http://news.southcn.com/community/", callback=self.parse_item_home, headers=self.header)  # 社会新闻
        yield scrapy.Request(url="http://kb.southcn.com/default.htm", callback=self.parse_item_home, headers=self.header)  # 南方快报
        yield scrapy.Request(url="http://news.southcn.com/g/node_74681.htm", callback=self.parse_item_home, headers=self.header)  # 权威公告

    def parse_item_home(self, response):
        detail_urls = response.xpath("""//div/div/div/div/div/h3/a/@href""").extract()
        for detail_url in detail_urls:
            time.sleep(random.uniform(1, 2))
            yield scrapy.Request(url=detail_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = str(response.xpath("""//*[@id="pubtime_baidu"]/text()""").extract()[0].strip())+":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("""//*[@id="content"]/p/text()""").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.southcn.com/"

            try:
                author_arr = response.xpath("""//*[@id="source_baidu"]/text()""").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "澎湃新闻"
                else:
                    author = author.replace("来源：","")
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title_arr = response.xpath("""//*[@id="article_title"]/text()""").extract()
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