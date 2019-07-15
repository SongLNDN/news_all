# coding=utf-8
import random

import scrapy
import re
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class cniiNews(scrapy.Spider):
    name = "cniiSpider"
    start_url = ["http://www.cnii.com.cn/node_33989.htm",
                 "http://www.cnii.com.cn/node_34000.htm",
                 "http://www.cnii.com.cn/telecom/node_34020.htm",
                 "http://www.cnii.com.cn/city/node_34051.htm"]
    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url=url, callback=self.parse_item_list_news,headers=self.header)
            # for page in range(2, 4):
            #     yield scrapy.Request(url=url.replace(".htm", "_" + str(page) + ".htm"),
            #                          callback=self.parse_item_list_news)

    def parse_item_list_news(self, response):
        url_arr = response.xpath("//ul[@class='list2']/li/a/@href").extract()
        for url in url_arr:
            time.sleep(random.uniform(1, 3))
            yield scrapy.Request(url=response.url.split("node")[0] + url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                # spiderUtil.log_level(8, response.url)
                pass
            try:
                content_arr = response.xpath("//div[@class='conzw']//text()").extract()
                content = "".join(content_arr).strip()
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                title_arr = response.xpath("//head/title//text()").extract()
                title = "".join(title_arr).split("_")[0]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//div[@class='conzz']//text()").extract()
                author = "".join(author_arr)
                if author == "":
                    author = "中国信息产业网"

            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.cnii.com.cn/"

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
                    # print(item)
                    yield item
            except:
                pass

        else:
            spiderUtil.log_level(response.status, response.url)