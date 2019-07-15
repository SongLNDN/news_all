# coding=utf-8
import scrapy
import re
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class iyiouNews(scrapy.Spider):
    name = "iyiouSpider"
    start_url = "https://www.iyiou.com/"

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_item_home)

    def parse_item_home(self, response):
        kinds_arr = response.xpath("//ul[@id='nav-industry']/li/a/@href").extract()
        for kinds in kinds_arr:
            yield scrapy.Request(url=kinds, callback=self.parse_item_page_list)

    def parse_item_page_list(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_list_news, dont_filter=True)
        # max_page = response.xpath("//a[@class='end']/text()").extract()[0]
        # for page in range(2,int(max_page)+1):
        #     list_news_url=response.url+str(page)+".html"
        #     yield scrapy.Request(url=list_news_url, callback=self.parse_item_list_news)

    def parse_item_list_news(self, response):
        url_arr = response.xpath("//div[@class='text fl']/a/@href").extract()
        for url in url_arr:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2})", response.text).group(0).replace("T",
                                                                                                                      " ") + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='post_description']")[0].xpath('string(.)').extract()
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                title = response.xpath("//head/title/text()").extract()[0][:-3]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//div[@id='post_author']/text()").extract()
                author = "".join(author_arr)
                if author == "":
                    author="亿欧网"
            except:
                spiderUtil.log_level(9, response.url)

            source = "https://www.iyiou.com/"

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
