import scrapy
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class e23News(scrapy.Spider):
    name = "e23Spider"
    start_url = "http://news.e23.cn/index.html"

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_item_home)

    def parse_item_home(self, response):
        kinds_arr = response.xpath("//div[@class='navl_k']/a/@href").extract()
        for kinds in kinds_arr:
            if kinds != "/index.html" and kinds != "/jinan/index.html":
                kinds_url = response.url[:-11] + kinds
                yield scrapy.Request(url=kinds_url, callback=self.parse_item_kinds)

    def parse_item_kinds(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_page_list, dont_filter=True)
        for page in range(2, 4):
            page_list_url = response.url.replace("index", str(page))
            yield scrapy.Request(url=page_list_url, callback=self.parse_item_page_list)

    def parse_item_page_list(self, response):
        news_url_list = response.xpath("//a/@href").extract()
        for news_url in news_url_list:
            if news_url.startswith("http") and news_url.endswith("html"):
                yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//div[@class='post_text']/p/text()").extract()
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                author = response.xpath("//head/meta[@name='author']/@content").extract()[0]
            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.e23.cn/"
            try:
                title = "".join(response.xpath("//head/title/text()").extract()[0].split("-")[:-2]).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                public_time = response.xpath("//div[@class='post_time']/p/text()").extract()[0]
            except:
                spiderUtil.log_level(8, response.url)

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
