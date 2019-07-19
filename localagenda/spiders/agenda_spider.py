import scrapy
from urllib.parse import urljoin

from localagenda.items import AgendaItem
from localagenda.cities import cities

class LinkSpider(scrapy.Spider):
    name="agenda"

    def start_requests(self):
        for city in cities:
            for meeting in city.get('Meetings').values():
                parser = getattr(self, "%s_parser" %(meeting.get('parser')), self.parse_method_not_found)
                yield scrapy.Request(meeting.get('url'), meta={
                    'city': city.get('Name'),
                    'meeting': meeting.get('name'),
                    'matcher': meeting.get('matcher')
                }, callback=parser)

    def parse_method_not_found(self):
        print("No parse method %s found!" %(self.i))

    def link_target_parser(self, response):
        href = response.xpath(response.meta.get('matcher')).attrib['href']
        target = urljoin(response.url, href)
        item = AgendaItem(content=href, target=target, city=response.meta.get('city'), meeting=response.meta.get('meeting'))
        return item
