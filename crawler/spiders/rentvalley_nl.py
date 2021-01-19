#
# This file was created by Maple Software
#
#
# This template is usable for TWO-LEVEL DEEP scrapers.
#
#
# HOW IT WORKS:
#
# 1. FOLLOWING: Follow the urls specified in rules.
# 2. SCRAPING: Scrape the fields and populate item.
#
#


from scrapy.loader.processors import MapCompose
from scrapy import Spider
from scrapy import Request
from scrapy.selector import Selector
from w3lib.html import remove_tags
from crawler.loader import MapleLoader
import json


class MySpider(Spider):
    name = 'rentvalley_nl'
    start_urls = ['https://www.rentvalley.nl/nl/realtime-listings/consumer']  # LEVEL 1

    # 1. FOLLOWING
    def parse(self, response):
        
        data = json.loads(response.body)
        
        for item in data:
            follow_url = response.urljoin(item["url"])
            lat = item["lat"]
            lng = item["lng"]
            ##yeni itemları ekle
            country=item["country"]
            rooms=item["rooms"]
            district=item["district"]
            zipcode=item["zipcode"]
            rentalsPrice=item["rentalsPrice"]

            yield Request(follow_url, callback=self.populate_item, meta={"lat":lat, "lng":lng,"country":country,"rooms":rooms,"district":district,"zipcode":zipcode,"rentalsPrice":rentalsPrice})


    # 2. SCRAPING level 2
    def populate_item(self, response):
        item_loader = MapleLoader(response=response)
        
        #// addvalue'de response ettik gerek yok//
        #lat = response.meta.get("lat")
        #lng = response.meta.get("lng")
        #country=response.meta.get("country")
        #rooms=response.meta.get("rooms")
        #district=response.meta.get("district")
        
        title = response.xpath("normalize-space(//h1/text())").extract_first()
        price=response.xpath("normalize-space(//dd/text())").extract_first()
        description=response.xpath("normalize-space(//p[@class='object-description']/text())").extract()
        square_meters=response.xpath("normalize-space(//dl[@class='full-details'][dt[.='Oppervlakte']]/dd/text())").extract_first()#sabit olarak Opper yazısının yanında her zaman duruyor şart koşulu kullanıldı.
        images = [response.urljoin(x)for x in response.xpath("//div[@class='responsive-slider-slide']/img/@src").extract()]
        
       

        #XPATH KISIM
        item_loader.add_value("price",price.split('p')[0])
        item_loader.add_value("title", title)
        item_loader.add_value("description", description)
        item_loader.add_value("square_meters", square_meters)
        item_loader.add_value("images",images)


        #ITEM SELECT KISIM
        item_loader.add_value("latitude",str(response.meta.get("lat")))##enlem
        item_loader.add_value("longtitude",str(response.meta.get("lng")))##boylam
        item_loader.add_value("room_count",str(response.meta.get("rooms")))##oda bilgisi
        item_loader.add_value("country",response.meta.get("country"))##ülke eklentisini items'a ekle
        item_loader.add_value("city",title.split(',')[-1])##city'i split et yukarı eklemeye gerek yok
        item_loader.add_value("address",title.split(',')[0])##adress split et yukarı eklemeye gerek yok
        item_loader.add_value("district",response.meta.get("district"))##ilçe
        item_loader.add_value("zipcode",response.meta.get("zipcode"))##zipkodu
        item_loader.add_value("external_link",response.url)##externallink
        item_loader.add_value("rent",str(response.meta.get("rentalsPrice")))##kiralama ücreti


        
        yield item_loader.load_item()