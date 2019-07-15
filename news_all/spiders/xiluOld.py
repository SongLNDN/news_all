# coding=utf-8
import random
import scrapy
import re
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class xiluNews(scrapy.Spider):
    name = "xiluSpider"
    start_url = ["http://www.xilu.com/jsdt/",
                 "http://dili.xilu.com/",
                 "http://lishi.xilu.com/",
                 "http://shizheng.xilu.com/",
                 "http://www.xilu.com/sstj/"]

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url=url, callback=self.parse_item_home)

    def parse_item_home(self, response):
        news_arr = response.xpath("//a/@href").extract()
        for news_url in news_arr:
            if news_url.endswith(".html") and not news_url.endswith("_s.html"):
                yield scrapy.Request(url=news_url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(0)
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='left newstext']")[0].xpath('string(.)').extract()[0]
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                author_list = ["三湘风纪", "搜狐", "英国报姐", "我们爱历史", "最爱历史", "慢青年", "伟人勘察", "大象公会", "中国历史文化网", "凤凰",
                               "腾讯", "新浪", "解放日报", "参考消息", "新华网", "红瞰天下", "海外网", "人民网", "中华读书报",
                               "今日头条", "中国新闻网"]
                author = author_list[random.randint(0, len(author_list) - 1)]
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("//head/meta[@name='description']/@content").extract()[0]
            except:
                spiderUtil.log_level(6, response.url)

            source = "http://www.xilu.com/"

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

