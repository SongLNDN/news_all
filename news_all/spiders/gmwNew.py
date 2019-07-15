# coding=utf-8
import scrapy
import re
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class youthNews(scrapy.Spider):
    name = "gmwSpider"
    url = ["http://news.gmw.cn/node_4705.htm",
           "https://news.gmw.cn/node_4108.htm",
          "http://news.gmw.cn/node_23548.htm",
          "http://news.gmw.cn/node_23707.htm",
          "http://news.gmw.cn/node_23547.htm",
          "http://news.gmw.cn/node_23545.htm",
           "http://news.gmw.cn/node_23708.htm",
           "http://news.gmw.cn/node_23709.htm"]

    def start_requests(self):
        for url in self.url:
            yield scrapy.Request(url=url, callback=self.parse_item_page_list)

    def parse_item_page_list(self, response):
        news_url_arr = response.xpath("//span[@class='channel-newsTitle']/a/@href").extract()
        for news_url in news_url_arr:
            if news_url.startswith("http:") and "content" in news_url:
                yield scrapy.Request(url=news_url, callback=self.parse)
            elif "content" in news_url:
                news_url = "https://news.gmw.cn/" + news_url
                yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//div[@class='u-mainText']//text()").extract()
                content = "".join(content_arr)
                # content = "".join(content_tmp2.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                info = response.xpath("//head/title/text()").extract()[0].replace('\t', '').replace('\n', '').replace(
                    '\r',
                    '').strip().split(
                    "_")
                title = info[0]
            except:
                spiderUtil.log_level(6, response.url)

            source = "http://www.gmw.cn/"

            try:
                author_arr = response.xpath("//head/meta[@name='author']/@content").extract()
                if author_arr == []:
                    author = "光明网"
                else:
                    author = author_arr[0]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                if content!="" and public_time.startswith(spiderUtil.get_first_hour()):

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

