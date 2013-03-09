import pymongo
from scrapy.conf import settings
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.http import Request
from scrapy.exceptions import DropItem
import re

# def uniqueList(seq):
#     seen = set()
#     seen_add = set.add
#     return [ x for x in seq if x not in seen and not seen_add(x)]

class ExtractLinkFromLog(object):
    def __init__(self, **kwargs):
        print "**********************************************"
        try:
            connection = pymongo.Connection(host=settings['MONGODB_SERVER'],
                                            port=settings['MONGODB_PORT'])
            print 'Database connected'
        except ConnectionFailure, e:
            sys.stderr.write("Cannot connect to mongodb: %s"%e)
            sys.exit(1)
        self.database = connection[settings["MONGODB_DATABASE"]]
        self.logCollection = self.database[settings["MONGODB_LOG_COLLECTION"]]
        self.wikiCollection = self.database[settings["MONGODB_WIKI_COLLECTION"]]

        newLogs = self.logCollection.find({"crawlFlag":False})
        pageID = []
        for log in newLogs:
            pageID.append(log["pageID"])
        pageID = list(set(pageID))

        self.data = []
        for id in pageID:
            page = self.wikiCollection.find_one({"pageID":id})
            if page is not None:
                p = {}
                p["pageID"] = id
                p["url"] = []
                tweets = page["tweets"]
                for tweet in tweets:
                    m = re.search('(?P<url>https?://[^\s]+)', tweet["text"])
                    if m:
                        p["url"].append(m.group("url"))
                self.data.append(p)

    def process_item(self, item, spider):
        print 'item1'
        return item

    def open_spider(self, spider):
        spider.data = self.data
        return

    def close_spider(self, spider):
        return


class TestPipeline(ImagesPipeline):
    # def __init__(self, **kwargs):
    #     print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    #     return
    
    def get_media_requests(self, item, info):
        for imageUrl in item["imageUrl"]:
            yield Request(imageUrl)
    
    def item_completed(self, results, item, info):
        f = open("out"+item["pageID"], 'aw+')
        images = [x for ok, x in results if ok]
        if not images:
            raise DropItem("Item contains no image")
        finalRecord = {}
        finalRecord["pageID"] = item["pageID"]
        finalRecord["url"] = item["url"]
        finalRecord["images"] = images
        f.write(str(finalRecord))
        f.write("\n")
        f.close()
        return item
