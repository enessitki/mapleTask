from scrapy import Spider

# We can add more functions
class BaseSpider(Spider):
    def debug(self, response):
        with open(self.name, "wb") as f:
            f.write(response.body)
