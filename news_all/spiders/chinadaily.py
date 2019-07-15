# coding=utf-8
import scrapy
import re
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class ceNews(scrapy.Spider):
    name = "chinadailySpider"
    start_url = ["http://china.chinadaily.com.cn/5bd5639ca3101a87ca8ff636",
                 "http://china.chinadaily.com.cn/5bd5639ca3101a87ca8ff62e",
                 "http://world.chinadaily.com.cn/5bd55927a3101a87ca8ff610",
                 "http://world.chinadaily.com.cn/5bda6641a3101a87ca904fe6",
                 "http://caijing.chinadaily.com.cn/finance/",
                 "http://cn.chinadaily.com.cn/lvyou/5b7628c6a310030f813cf48a",
                 "http://cn.chinadaily.com.cn/lvyou/5b7628c6a310030f813cf48c",
                 "http://cn.chinadaily.com.cn/lvyou/5b7628c6a310030f813cf48b",
                 "http://cn.chinadaily.com.cn/lvyou/5b7628c6a310030f813cf493",
                 "http://cn.chinadaily.com.cn/lvyou/5bac7d20a3101a87ca8ff52d",
                 "http://fashion.chinadaily.com.cn/5b762404a310030f813cf467",
                 "http://cn.chinadaily.com.cn/jiankang",
                 "http://fashion.chinadaily.com.cn/5b762404a310030f813cf461",
                 "http://fashion.chinadaily.com.cn/5b762404a310030f813cf462",
                 "http://fashion.chinadaily.com.cn/5b762404a310030f813cf463",
                 "http://fashion.chinadaily.com.cn/5b8f77a7a310030f813ed4c8"]
    header = spiderUtil.header_util()

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url=url, callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        for page in range(1, 2):
            if response.url.endswith("/"):
                list_url = response.url + "page_" + str(page) + ".html"
                yield scrapy.Request(url=list_url, callback=self.parse_item_list_news)
            else:
                list_url = response.url + "/page_" + str(page) + ".html"
                yield scrapy.Request(url=list_url, callback=self.parse_item_list_news)

    def parse_item_list_news(self, response):
        url_arr = response.xpath("//h3/a/@href").extract()
        for url in url_arr:
            url = "http:" + url
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//div[@id='Content']//text()").extract()
                content = "".join(content_arr).strip()
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                title_arr = response.xpath("//head/title//text()").extract()
                title = "".join(title_arr).strip().strip()[:-8]
            except:
                spiderUtil.log_level(6, response.url)
            try:
                author = response.xpath("//head/meta[@name='author']/@content").extract()
                if author == []:
                    author = "中国日报网"
                else:
                    author = author[0]
            except:
                spiderUtil.log_level(9, response.url)
            source = "http://www.chinadaily.com.cn/"

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0)+":00"
            except:
                # spiderUtil.log_level(8, response.url)
                pass
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
