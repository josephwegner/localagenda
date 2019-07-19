import scrapy

class AgendaItem(scrapy.Item):
    content = scrapy.Field()
    target = scrapy.Field()
    meeting = scrapy.Field()
    city = scrapy.Field()
