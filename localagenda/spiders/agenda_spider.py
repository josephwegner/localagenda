import scrapy
import copy
import re
from urllib.parse import urljoin, urlparse, urlunparse

from localagenda.items import AgendaItem
from localagenda.cities import cities

class LinkSpider(scrapy.Spider):
    name="agenda"

    def start_requests(self):
        for city in cities:
            if 'Meetings' in city and (not hasattr(self, 'city') or city.get('Name') == self.city):
                for meeting in city.get('Meetings'):
                    parser = getattr(self, "%s_parser" %(meeting.get('parser')), self.parse_method_not_found)
                    yield scrapy.Request(meeting.get('url'), cookies=meeting.get('cookies'), meta={
                        'city': city.get('Name'),
                        'meeting': meeting.get('name'),
                        'matcher': meeting.get('matcher'),
                        'extract': meeting.get('extract'),
                        'dont_obey_robotstxt': True
                    }, callback=parser)

    def parse_method_not_found(self):
        print("No parse method %s found!" %(self.i))

    def extract(self, node, extract):
        if extract is None or extract == 'href':
            return node.attrib['href']
        else:
            attr = list(extract.keys())[0]
            val = node.attrib[attr]
            finder = re.compile(extract[attr])
            search = finder.search(val)

            if search is None:
                return None

            return search.group(1)

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
        matcher = response.meta.get('matcher')

        if isinstance(matcher, str):
            xpath = "//a[contains(text(), '%s')]" %(matcher)
        else:
            if 'start' in matcher:
                xpath = "//a[starts-with(text(), '%s')]" %(matcher['start'])
            elif 'end' in matcher:
                xpath = "//a[substring(text(), string-length(text()) - string-length('%s') +1) = '%s']" %(matcher['end'], matcher['end'])
            else:
                return None

        node = response.xpath(xpath)
        if isinstance(matcher, dict) and 'not' in matcher:
            for anchor in node:
                if matcher['not'] in node.xpath("./text()").get():
                    node.remove(anchor)

        if len(node) == 0:
            return None


        href = self.extract(node, response.meta.get('extract'))
        if href is None:
            return None

        target = self.full_url(response, href)
        item = AgendaItem(content=href, target=target, city=response.meta.get('city'), meeting=response.meta.get('meeting'))
        return item

    def xpath_css_parser(self, response):
        doc = self.parse_with_matchers(response, response.meta.get('matcher'))

        if doc == None:
            return None

        href = self.extract(doc, response.meta.get('extract'))
        if href is None:
            return None

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
