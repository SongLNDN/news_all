# coding=utf-8
import json
import scrapy
import re
import sys
from news_all.items import NewsAllItem
from news_all.spiders.util import spiderUtil


class cyolOld(scrapy.Spider):
    name = "cyolSpider"
    ids = {767, 548, 777, 885, 895, 886, 785, 797, 803, 804, 811, 812, 814, 818, 826,
           834, 837, 842, 550, 849}
    header=spiderUtil.header_util()

    def start_requests(self):
        tmp = "https://zqbapp.cyol.com/zqzxapi/api.php?s=/Web/getNewsListCache/version/3.0.8/tid/%s/page/%s"
        for id in self.ids:
            for page in range(1, 2):
                url = tmp % (id, page)
                yield scrapy.Request(url=url, callback=self.parse_item_news_list,headers=self.header)

    def parse_item_news_list(self, response):
        p = re.compile(r'[(](.*)[)]', re.S)
        r = re.findall(p, response.body.decode('utf-8'))[0]
        json_loads = json.loads(r)
        data = json_loads["data"]
        for i in data:
            newsurl = i['newsurl']
            yield scrapy.Request(url=newsurl, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)
            try:
                content_arr = response.xpath("//div[@class='section-main']/p/text()").extract()
                content = "".join(content_arr)
                # content = "".join(content_tmp.split())
            except:
                spiderUtil.log_level(7, response.url)

            try:
                public_time = re.search(r"(\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0) + ":00"
                public_time = response.url.split("/")[-3][:-2] + "-" + public_time
            except:
                # spiderUtil.log_level(8, response.url)
                pass

            try:
                title_arr = response.xpath("//head/title//text()").extract()
                title = "".join(title_arr).strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                author_arr = response.xpath("//span[@id='copyfrom']//text()").extract()
                author = "".join(author_arr).strip()
                if author == "":
                    author = "中青在线"
            except:
                spiderUtil.log_level(9, response.url)

            source = "http://www.cyol.com/"

            try:
                if content != "" and len(content) >= 100 and public_time.startswith(spiderUtil.get_first_hour()):

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
