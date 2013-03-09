from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import HtmlXPathSelector
from cs3281.items import PageAnalytic
import subprocess
import os

class AnalyticSpider(BaseSpider):
    name = "analytic"
    data = []
    start_urls = []
    
    def __init__(self, **kwargs):
        return

    def start_requests(self):
        for page in self.data:
            print page["pageID"]
            for url in page["url"]:
                yield Request(url,meta={'url':url, 'pageID':page["pageID"]})

    def parse(self, response):
        # print "MT",response.request.meta
        meta = response.request.meta
        hxs = HtmlXPathSelector(response)
        images = hxs.select('//img')
        imageLink = []
        for image in images:
            src = image.select('@src').extract()[0]
            if src.startswith('/'):
                src = response.request.url+src
            imageLink.append(src)
            #print meta["url"],"src is",src
        item = PageAnalytic()
        item["pageID"] = meta["pageID"]
        item["url"] = response.request.url
        item["imageUrl"] = imageLink
        return item
