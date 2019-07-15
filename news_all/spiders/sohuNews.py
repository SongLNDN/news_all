#!/usr/bin/env python 
# encoding: utf-8 


"""
 Created by songyao@mail.ustc.edu.cn on 2019/7/9 上午11:36
 
 Function: 搜狐新闻爬虫
 
"""
import json
import scrapy
import sys
import urllib
from datetime import datetime
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class sohuNews(scrapy.Spider):
    name = "sohuNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        url_list=[15,10,9,8,17,18,19,23,24,25,26,27,28,29,30,34,38,39,40,41,42,43,44,45,46,47]
        for i in url_list:
            url = 'http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId='+str(i)+'&page=1&size=80'
            yield scrapy.Request(url=url, callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        url = response.url
        request = urllib.request.Request(url)
        data_str = urllib.request.urlopen(request, timeout=10).read()
        data_str = data_str.decode('utf-8')
        data_str = data_str[1:-1]
        data_str = eval(data_str, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        data_str = json.dumps(data_str)
        data_str = json.loads(data_str)
        for r in data_str:
            try:
                public_time_rt = datetime.fromtimestamp(r['publicTime'] // 1000)
                public_time = datetime.strftime(public_time_rt, '%Y-%m-%d %H:%M:%S')
            except:
                spiderUtil.log_level(8, response.url)
            try:
                author = str(r['authorName'])
            except:
                spiderUtil.log_level(9, response.url)
            try:
                title = str(r['title'])
            except:
                spiderUtil.log_level(6, response.url)
            url = 'http://www.sohu.com/a/' + str(r['id']) + '_' + str(r['authorId'])

            yield scrapy.Request(url=url, callback=self.parse, headers=self.header, meta={'public_time':public_time,'url':url,'title':title,'author':author})

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                content_arr = response.xpath("""//article//p//text()""").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://news.sohu.com/"

            try:
                if content != "" and str(response.mete['public_time']).startswith(spiderUtil.get_first_hour()):
                    item = NewsAllItem()
                    item["public_time"] = response.mete['public_time']
                    item["url"] = response.mete['url']
                    item["title"] = response.mete['title']
                    item["author"] = response.mete['author']
                    item["source"] = source
                    item["content"] = content
                    item["html_size"] = html_size
                    item["crawl_time"] = spiderUtil.get_time()
                    # print(self.item)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)



