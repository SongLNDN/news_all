# coding=utf-8
import scrapy
import re
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class legaldailyNew(scrapy.Spider):
    name = "legaldailySpider"
    start_url = {"http://www.legaldaily.com.cn/leader/node_34048.htm",
                 "http://www.legaldaily.com.cn/commentary/node_34228.htm",
                 "http://www.legaldaily.com.cn/rdlf/node_33988.htm",
                 "http://www.legaldaily.com.cn/legal_case/node_81768.htm",
                 "http://www.legaldaily.com.cn/army/node_80548.htm",
                 "http://www.legaldaily.com.cn/Finance_and_Economics/node_75668.htm",
                 "http://www.legaldaily.com.cn/fxjy/node_89845.htm",
                 "http://www.legaldaily.com.cn/government/node_81785.htm",
                 "http://www.legaldaily.com.cn/international/node_81908.htm",
                 "http://www.legaldaily.com.cn/integrity-observe/node_42748.htm",
                 "http://www.legaldaily.com.cn/IT/node_69448.htm"}

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url=url, callback=self.parse_item_home)

    def parse_item_home(self, response):
        news_list_arr = response.xpath("//a/@href").extract()
        for news_list in news_list_arr:
            if "node_" in news_list and news_list.endswith(".htm"):
                yield scrapy.Request(url=news_list, callback=self.parse_item_news_page)

    def parse_item_news_page(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_news_list, dont_filter=True)

    def parse_item_news_list(self, response):
        news_url_arr = response.xpath("//dd[@class='dd6401']/a/@href").extract()
        for news_url in news_url_arr:
            if "content_" in news_url:
                yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//dl/dd[@id='CONTENT']/p//text()").extract()
                content = "".join(content_arr).replace("\xa0", "")
            except:
                spiderUtil.log_level(7, response.url)

            try:
                title_arr = response.xpath("//dd[@class='f18 b black02 yh center']//text()").extract()
                title = "".join(title_arr).strip()
                if title=="":
                    title_arr = response.xpath("//td[@class='f22 b black02']//text()").extract()
                    title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                author_arr = response.xpath("//dd[@class='f12 black02']//text()").extract()
                author_tmp = "".join(author_arr).strip()
                if author_tmp == "":
                    author = "法制网"
                else:
                    author = author_tmp
            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.legaldaily.com.cn/"

            try:
                if len(content) > 80 and public_time.startswith(spiderUtil.get_first_hour()):
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
