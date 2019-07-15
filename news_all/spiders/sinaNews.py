#!/usr/bin/env python
# encoding: utf-8


"""
 Created by songyao@mail.ustc.edu.cn on 2019/4/26 下午2:34

 Function: 新浪新闻爬虫

"""
import requests
import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class sinaNews(scrapy.Spider):
    name = "sinaNewsSpider"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url="https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page=1", callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        response = requests.get(response.url, headers=self.header)
        data = response.json()
        datas = data['result']['data']
        for dict_data in datas:
            yield scrapy.Request(url=dict_data['url'], callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                if response.xpath("""//*[@id="top_bar"]/div/div/span[1]/text()""").extract():
                    content_time = response.xpath("""//*[@id="top_bar"]/div/div/span[1]/text()""").extract()
                    public_datetime = str(content_time[0]).replace("年", "-").replace("月", "-").replace("日", "")
                    public_time = public_datetime + ":00"
                else:
                    if response.xpath("""//*[@id="top_bar"]/div/div[2]/span/text()""").extract():
                        content_time = response.xpath("""//*[@id="top_bar"]/div/div[2]/span/text()""").extract()
                        public_datetime = str(content_time[0]).replace("年", "-").replace("月", "-").replace("日", "")
                        public_time = public_datetime + ":00"
                    else:
                        content_time = response.xpath("""//*[@id="pub_date"]/text()""").extract()
                        public_datetime = str(content_time[0]).replace("年", "-").replace("月", "-").replace("日", " ")
                        public_time = public_datetime + ":00"

            except:
                spiderUtil.log_level(8, response.url)

            try:
                if response.xpath("""//*[@id="artibody"]/p/text()""").extract():
                    content_arr = response.xpath("""//*[@id="artibody"]/p/text()""").extract()
                else:
                    content_arr = response.xpath("""//*[@id="article"]/p/text()""").extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            source = "https://news.sina.com.cn/"

            try:
                if response.xpath("""//span[@class="source"]""").extract()[0]:
                    author = response.xpath("""//span[@class="source"]""").extract()[0].strip()
                else:
                    author = "新浪网"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                if response.xpath("""/html/body/div/h1/text()""").extract()[0]:
                    title = response.xpath("""/html/body/div/h1/text()""").extract()[0]
                else:
                    title = response.xpath("""//*[@id="artibodyTitle"]/text()""").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                if content != "" and public_time.startswith(spiderUtil.get_first_hour()):
                # if content != "":
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













