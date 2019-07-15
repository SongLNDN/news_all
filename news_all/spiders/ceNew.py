import scrapy
import sys
import re
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class ceNews(scrapy.Spider):
    name = "ceSpider"
    start_url = "http://intl.ce.cn/"
    header = spiderUtil.header_util()

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        kinds_arr = response.xpath("//div[@class='ceallnava']/ul/li/a/@href").extract()
        for kinds in kinds_arr:
            if kinds != "http://intl.ce.cn/specials/":
                yield scrapy.Request(url=kinds, callback=self.parse_item_kinds)

    def parse_item_kinds(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_item_page_list, dont_filter=True)

    def parse_item_page_list(self, response):
        news_url_arr = response.xpath("//span[@class='f1']/a/@href").extract()
        for news_url in news_url_arr:
            if news_url.startswith("http") and "more" not in news_url:
                yield scrapy.Request(url=news_url, callback=self.parse)
            else:
                head = response.url.split("/")
                if news_url.startswith("../../"):
                    news_url = "/".join(head[:3]) + "/" + news_url.replace("../../", "")
                    yield scrapy.Request(url=news_url, callback=self.parse)
                elif news_url.startswith("../"):
                    news_url = "/".join(head[:4]) + "/" + news_url.replace("../", "")
                    yield scrapy.Request(url=news_url, callback=self.parse)
                elif news_url.startswith("./"):
                    news_url = response.url.split("index")[0] + news_url.replace("./", "")
                    yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//div[@id='articleText']//text()").extract()
                content = "".join(content_arr).strip()
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                public_time = (re.search(r"(\d{4}年\d{1,2}月\d{1,2}日\s\d{1,2}:\d{1,2})", response.text).group(
                    0) + ":00").replace(
                    "年", "-").replace("月", "-").replace("日", "")
            except:
                spiderUtil.log_level(8, response.url)

            source = "http://www.ce.cn/"
            try:
                title = response.xpath("//head/title/text()").extract()[0].split("_")[0]
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author = response.xpath("//head/meta[@name='author']/@content").extract()[0]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                if public_time.startswith(spiderUtil.get_first_hour()) and content != "":
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
