# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys

from news_all.spiders.util import spiderUtil


class NewsAllPipeline(object):
    def process_item(self, item, spider):
        source = item["source"]
        content = item["content"]
        public_time = item["public_time"]
        url = item["url"]
        title = item["title"]
        author = item["author"]
        crawl_time = item["crawl_time"]
        html_size = item["html_size"]

        dict = spiderUtil.get_polarity_keyword(content, url)
        negative = dict.get("negative")
        positive = dict.get("positive")
        polarity = dict.get("polarity")
        keywords = dict.get("keywords")
        summary = dict.get("summary")
        keyword_md5 = dict.get("keyword_md5")

        es_index = "news_data"
        data_id = ""
        source_type = "新闻"
        domain = "政府"
        praise_num = ""
        if keyword_md5 != "d41d8cd98f00b204e9800998ecf8427e":
            ip = spiderUtil.get_local_ip()

            text2es = str(title) + str(source) + str(data_id) + str(author) + str(public_time) + str(domain) + str(
                url) + str(ip) + str(crawl_time) + str(negative) + str(polarity) + str(positive) + str(keywords) + str(
                summary) + str(source_type) + str(keyword_md5)
            es_size = sys.getsizeof(text2es)

            data = es_index + "|&|" + \
                   str(es_size) + "|&|" + \
                   crawl_time + "|&|" + \
                   url + "|&|" + \
                   ip + "|&|" + \
                   title + "|&|" + \
                   source + "|&|" + \
                   author + "|&|" + \
                   public_time + "|&|" + \
                   content + "|&|" + \
                   str(html_size) + "|&|" + \
                   negative + "|&|" + \
                   positive + "|&|" + \
                   polarity + "|&|" + \
                   praise_num + "|&|" + \
                   keywords + "|&|" + \
                   keyword_md5 + "|&|" + \
                   data_id + "|&|" + \
                   source_type + "|&|" + \
                   domain + "|&|" + \
                   summary

            from pykafka import KafkaClient
            # client = KafkaClient(hosts="10.6.6.67:9092,10.6.6.69:9092,10.6.6.70:9092,10.6.6.71:9092,10.6.6.73:9092")
            client = KafkaClient(hosts="192.168.1.162:9092")
            # 查看所有topic
            print(client.topics)
            topic = client.topics['test_topic']  # 选择一个topic
            # 同步发送数据
            with topic.get_sync_producer() as producer:
                # 数据转换成byte才可以发送
                producer.produce(bytes(data, encoding="utf8"))
                print("end")
        # def productList(rows):
        #     string = ''
        #     # 将多条数据放入list中
        #     strings = []
        #     count = 0
        #     for row in rows:
        #         file = urllib.request.urlopen(row[2], timeout=5)
        #
        #         try:
        #             data = file.read()
        #             # 是否被封号，从偏移量3000的位置往下找
        #             isBan = str(data).find('被封号的字符串', 3000)
        #             if (isBan != -1):
        #                 string = 'ip被封'
        #             else:
        #                 selector = etree.HTML(data)
        #                 data = selector.xpath('//*[@id="zhengwen"]/p/span/text()')
        #                 # 将获取到的多个正文内容拼接成一条字符串
        #                 for i in data:
        #                     if (i != None):
        #                         string = string + i
        #
        #                         # 打印查看
        #             print('正文：', string)
        #             # 将数据库中一条数据的多个字段通过 -.- 拼接到一起
        #             content = row[0] + '-.-' + row[1] + '-.-' + string + '-.-' + row[3] + '-.-' + row[4]
        #             # 放入list中
        #             strings.append(content)
        #             # 清空字符串
        #             string = ''
        #             print("集合：", strings)
        #             print("集合长度：", len(strings))
        #             count = count + 1
        #             # 每十条数据就调用一次kafka生产者的代码
        #             if (count >= 10):
        #                 print('进入到insertManyRow')
        #                 TestspiderPipeline.insertManyRow(strings)
        #                 strings = []
        #                 count = 0
        #         except Exception as e:
        #             print("线程出错：%s" % (e))
