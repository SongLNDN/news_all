#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/7/9 下午4:34
 
 Function: 新华网爬虫
 
"""


import json
import scrapy
import sys
from datetime import datetime
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class sohuNews(scrapy.Spider):
    name = "xinhuaNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        url = 'http://qc.wa.news.cn/nodeart/list?nid=11147664&pgnum={}&cnt={}&tp=1&orderby=1'
        num = 30000
        pgnum = 1
        while num / 200 > 0:
            cnt = (num - 1) % 200 + 1
            url = str(url).format(pgnum, cnt)
            pgnum += 1
            num -= cnt
            yield scrapy.Request(url=url, callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        data_str = response.text
        data_str = data_str[1:-1]
        data_str = eval(data_str, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        data_str = json.dumps(data_str)
        data_str = json.loads(data_str)
        data_str = data_str['data']['list']
        for r in data_str:
            try:
                public_time = datetime.strptime(r['PubTime'], '%Y-%m-%d %H:%M:%S')
            except:
                spiderUtil.log_level(8, response.url)
            try:
                author = str(r['Author'])
            except:
                spiderUtil.log_level(9, response.url)
            try:
                title = str(r['Title'])
            except:
                spiderUtil.log_level(6, response.url)
            r_url = r['LinkUrl']
            public_time = public_time
            title = title
            author = author
            yield scrapy.Request(url=r_url, callback=self.parse, headers=self.header, meta={"public_time":public_time,"title":title, "author":author})

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_arr = response.xpath("""//div[contains(@id,'detail')]//p/text()""").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.xinhuanet.com/"

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



