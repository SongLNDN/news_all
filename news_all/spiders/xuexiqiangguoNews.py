#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/7/9 下午5:28
 
 Function: 学习强国爬虫
 
"""



import json
import scrapy
import sys
from datetime import datetime
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class sohuNews(scrapy.Spider):
    name = "xuexiqiangguoNewsSpider"
    header = spiderUtil.header_util()
    item = NewsAllItem()

    def start_requests(self):
        home_url = 'https://www.xuexi.cn/lgdata/1jscb6pu1n2.json?_st=26044379'
        yield scrapy.Request(url=home_url, callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        data_str = response.text
        data_str = data_str[1:-1]
        data_str = eval(data_str, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        data_str = json.dumps(data_str)
        data_str = json.loads(data_str)
        for r in data_str:
            try:
                public_time = str(r['publishTime'])
            except:
                spiderUtil.log_level(8, response.url)
            try:
                author = str(r['source'])
            except:
                spiderUtil.log_level(9, response.url)
            try:
                title = str(r['title'])
            except:
                spiderUtil.log_level(6, response.url)
            try:
                r_url1 = str(r_url).split("id=")[-1]
                r_url = "https://boot-source.xuexi.cn/data/app/"+r_url1+".js?callback=callback"
                yield scrapy.Request(url=r_url, callback=self.parse, headers=self.header,meta={"public_time": public_time, "title": title, "author": author})
            except:
                pass



    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            data_str = response.text
            data_str = data_str[9:-1]
            data_str = eval(data_str, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
            data_str = json.dumps(data_str)
            data_str = json.loads(data_str)
            try:
                content = str(data_str['normalized_content'])
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.xuexi.cn/"

            try:
                if content != "" and str(response.meta["public_time"]).startswith(spiderUtil.get_first_hour()):
                # if content != "" :
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



