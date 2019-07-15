# coding=utf-8
import random
import scrapy
import re
import sys
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class cyolOld(scrapy.Spider):
    name = "k618Spider"
    start_url = "http://news.k618.cn/roll/"

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_item_news_list)

    def parse_item_news_list(self, response):
        news_url_arr = response.xpath("//a/@href").extract()
        for news_url in news_url_arr:
            if news_url.endswith(".html") and "jhtj" not in news_url:
                if spiderUtil.get_time().replace("-", "")[:8] in news_url:
                    time.sleep(random.uniform(1, 2))
                    yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//div[@class='TRS_Editor']")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
            except:
                spiderUtil.log_level(7, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                author = response.xpath("//head/meta[@name='author']/@content").extract()[0]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("//head/title/text()").extract()[0].split("_")[0]
            except:
                spiderUtil.log_level(6, response.url)

            source = "http://www.k618.cn/"

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
