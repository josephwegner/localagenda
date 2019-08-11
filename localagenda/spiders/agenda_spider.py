import scrapy
from urllib.parse import urljoin

from localagenda.items import AgendaItem
from localagenda.cities import cities

class LinkSpider(scrapy.Spider):
    name="agenda"

    def start_requests(self):
        for city in cities:
            for meeting in city.get('Meetings'):
                parser = getattr(self, "%s_parser" %(meeting.get('parser')), self.parse_method_not_found)
                yield scrapy.Request(meeting.get('url'), meta={
                    'city': city.get('Name'),
                    'meeting': meeting.get('name'),
                    'matcher': meeting.get('matcher')
                }, callback=parser)

    def parse_method_not_found(self):
        print("No parse method %s found!" %(self.i))

    def link_with_text_parser(self, response):
        xpath = "//a[starts-with(text(), '%s')]" %(response.meta.get('matcher'))
        node = response.xpath(xpath)
        if len(node) == 0:
            return None

        href = node.attrib['href']
        target = urljoin(response.url, href)
        item = AgendaItem(content=href, target=target, city=response.meta.get('city'), meeting=response.meta.get('meeting'))
        return item

    def xpath_css_parser(self, response):
        parse_with_matchers(response, response.meta.get('matcher'))

        href = current_document.attrib['href']
        target = urljoin(response.url, href)
        item = AgendaItem(content=href, target=target, city=response.meta.get('city'), meeting=response.meta.get('meeting'))
        return item

    def parse_with_matchers(doc, matchers):
        step = matchers.pop(0)

        if not doc:
            return None

        if 'xpath' in step:
            returned_document = doc.xpath(step['xpath'])
        else:
            returned_document = doc.css(step['css'])


        if len(returned_document) == 0:
            return None
        else:
            
