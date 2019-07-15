# coding=utf-8
import scrapy
import time
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil
import sys


class stnnNews(scrapy.Spider):
    name = "stnnSpider"
    strat_url = "http://www.stnn.cc/"
    head = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "Hm_lvt_699058f519fef8e655be3440c145bc25=1553480323; Hm_lpvt_699058f519fef8e655be3440c145bc25=1553480330",
            "Host": "www.stnn.cc",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    def start_requests(self):
        yield scrapy.Request(url=self.strat_url, callback=self.parse_item_kinds_news, headers=self.head)

    # 获取几大分类的新闻页面
    def parse_item_kinds_news(self, response):
        kinds_news = response.xpath("//ul[@style='padding-top:18px; padding-bottom:5px']/a/@href").extract()
        for news_page in kinds_news:
            if news_page != "http://tu.stnn.cc/" and news_page != "http://www.stnn.cc":
                yield scrapy.Request(url=news_page, callback=self.parse_item_news_page)

    # 获取每个分类的所有新闻
    def parse_item_news_page(self, response):
        new_url_list = response.xpath("//ul[@class='box1']/li/a/@href").extract()
        for new_url in new_url_list:
            time.sleep(1)
            yield scrapy.Request(url=new_url, callback=self.parse, meta={"url": new_url})

    # 具体每篇新闻内容获取
    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            # 标题解析
            try:
                title = response.xpath("//h1[@class='article-title']/text()").extract()[0].replace('\t', '').replace('\n',
                                                                                                                                    '').replace(
                        '\r', '')
            except:
                spiderUtil.log_level(6, response.url)

            try:
                public_time_tmp = response.xpath("//div[@class='article-infos']/span[@class='date']/text()").extract()[0]
                if len(public_time_tmp) == 16:
                    public_time = public_time_tmp + ":00"
                else:
                    public_time = public_time_tmp
            except:
                spiderUtil.log_level(8, response.url)

            source ="http://www.stnn.cc/"
            try:
                content_arr = response.xpath("//div[@class='article-content fontSizeSmall BSHARE_POP']/p/text()").extract()
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)
            try:
                if content != "" and public_time.startswith(spiderUtil.get_first_hour()):
                    item = NewsAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = public_time
                    item["url"] = response.meta["url"]
                    item["title"] = title
                    item["author"] = "星岛环球网"
                    item["crawl_time"] = spiderUtil.get_time()
                    item["html_size"] = html_size
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)