# coding=utf-8
import json
import random
import scrapy
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class wenweipoNews(scrapy.Spider):
    name = "wenweipoSpider"
    start_url = "http://news.wenweipo.com/list_news.php?oldnews=1&instantCat=%s&date=%s"

    def start_requests(self):
        area_arr = ["china", "hk", "world"]
        for area in area_arr:
            url = self.start_url % (area, spiderUtil.get_time()[:10])
            yield scrapy.Request(url=url, callback=self.parse_item_home)

    def parse_item_home(self, response):
        json_load = json.loads(response.body)
        for i in json_load:
            url = i.get("link")
            today_date = response.url[-10:]
            today_time = i.get("date")[4:]
            public_time = today_date + " " + today_time + ":00"
            if public_time.startswith(spiderUtil.get_first_hour()) and len(public_time) == 19:
                time.sleep(random.uniform(2, 3))
                yield scrapy.Request(url=url, callback=self.parse, meta={"public_time": public_time})

    def parse(self, response):
        if response.status==200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//div[@id='main-content']")[0].xpath('string(.)').extract()[0]
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                public_time = response.meta["public_time"]
            except:
                spiderUtil.log_level(8, response.url)

            try:
                author = response.xpath("//p[@class='fromInfo']/text()").extract()[0].split("：")[1]
            except:
                spiderUtil.log_level(9, response.url)
            try:
                    title = response.xpath("//head/meta[@name='title']/@content").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)
            source = "http://www.wenweipo.com/"

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
                    # 数据打入piplines处理
                    yield item

            except:
                pass

        else:
            spiderUtil.log_level(response.status, response.url)

