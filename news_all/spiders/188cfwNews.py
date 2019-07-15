# !/usr/bin/env python
# encoding: utf-8


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午4:08

 Function: 188财富网

"""
import random

import re
import time
import scrapy
import sys


from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class xuanjiangjiaNews(scrapy.Spider):
    name = "188cfwNewsSpider"
    start_url = "http://www.188cf.net/"
    header = spiderUtil.header_util()

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'Accepy': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Host': 'www.188cf.net',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'http://www.188cf.net/'
        }
        Cookie = {
            'security_session_verify': '87456e2f5288fc9e54c5508487c724ae',
            'security_session_mid_verify': '2a568bbe22a10d992a688d95dc309586'
        }

        yield scrapy.Request(url="http://www.188cf.net/gegu/", callback=self.parse_item_home, headers=headers, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/gupiao/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/licai/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/jijin/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/qihuo/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/huangjin/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/waihui/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/zhaiquan/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/caijing/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/yinhang/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)
        # yield scrapy.Request(url="http://www.188cf.net/xueyuan/", callback=self.parse_item_home,headers=self.header, cookies=Cookie)

    def parse_item_home(self, response):
        detail_urls = response.xpath("""//div[@class="bt"]//@href""").extract()
        for detail_url in detail_urls:
            print(detail_url)
            time.sleep(random.uniform(1, 2))
            yield scrapy.Request(url=detail_url, callback=self.parse_item_home, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_time = response.xpath("""//div[@class="info"]//text()""").extract()
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", content_time[0]).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arrs = response.xpath("""//td[@class="content"]//p//text()""").extract()
                content_arr = content_arrs.split('推荐信息')[0]
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.188cf.net/"

            try:
                author = "188财富网"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("""//h1//text()""").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                if content != "" and str(public_time).startswith(spiderUtil.get_first_hour()):
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

