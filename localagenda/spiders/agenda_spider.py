import scrapy
import copy
from urllib.parse import urljoin, urlparse, urlunparse

from localagenda.items import AgendaItem
from localagenda.cities import cities

class LinkSpider(scrapy.Spider):
    name="agenda"

    def start_requests(self):
        for city in cities:
            if 'Meetings' in city:
                for meeting in city.get('Meetings'):
                    parser = getattr(self, "%s_parser" %(meeting.get('parser')), self.parse_method_not_found)
                    yield scrapy.Request(meeting.get('url'), cookies=meeting.get('cookies'), meta={
                        'city': city.get('Name'),
                        'meeting': meeting.get('name'),
                        'matcher': meeting.get('matcher'),
                        'dont_obey_robotstxt': True
                    }, callback=parser)

    def parse_method_not_found(self):
        print("No parse method %s found!" %(self.i))

    def full_url(self, response, href):
        base = response.css('base')
        if len(base) > 0:
            url = urljoin(base[0].attrib['href'], href)
        else:
            url = urljoin(response.url, href)

        parts = urlparse(url)
        if parts.scheme == '':
            lst = list(parts)
            lst[0] = 'https'
            parts = tuple(lst)

        return urlunparse(parts)

    def link_with_text_parser(self, response):
        xpath = "//a[starts-with(text(), '%s')]" %(response.meta.get('matcher'))
        node = response.xpath(xpath)
        if len(node) == 0:
            return None

        href = node.attrib['href']
        target = self.full_url(response, href)
        item = AgendaItem(content=href, target=target, city=response.meta.get('city'), meeting=response.meta.get('meeting'))
        return item

    def xpath_css_parser(self, response):
        doc = self.parse_with_matchers(response, response.meta.get('matcher'))

        if doc == None:
            return None

        href = doc.attrib['href']
        target = self.full_url(response, href)
        item = AgendaItem(content=href, target=target, city=response.meta.get('city'), meeting=response.meta.get('meeting'))
        return item

    def parse_with_matchers(self, doc, matchers):
        step = matchers.pop(0)

        if not doc:
            return None


        if 'xpath' in step:
            returned_document = doc.xpath(step['xpath'])
        else:
            returned_document = doc.css(step['css'])

        if len(returned_document) == 0:
            return None
        elif len(matchers) == 0:
            return returned_document
        else:
            for doc in returned_document:
                new_matchers = copy.deepcopy(matchers)
                traversed = self.parse_with_matchers(doc, new_matchers)
                if traversed != None:
                    return traversed

            # If none of the above docs returns anything, just return none
            return None
