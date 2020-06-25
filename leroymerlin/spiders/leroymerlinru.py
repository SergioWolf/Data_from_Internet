### -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader

class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']
    count_page = 1

    def __init__(self, sections):
      self.start_urls = [f'https://spb.leroymerlin.ru/search/?q={section}' for section in sections]


    def parse(self, response:HtmlResponse):
        next_page_link = response.xpath('//a[@class="paginator-button next-paginator-button"]/@href').extract_first()
        # next_page_link = response.xpath('//a[@class="paginator-button next-paginator-button"]')
        # print(next_page_link)
        if next_page_link != None:
            next_page_link_1 = 'https://spb.leroymerlin.ru' + next_page_link
            # print(next_page_link_1)
            # print(1)
            items_links = response.xpath('//div[@class="product-name"]//a')
            for link in items_links:
                 yield response.follow(link, callback=self.parse_item)
            self.count_page += 1

            yield response.follow(next_page_link_1, callback=self.parse)
        else:
            print('Сбор данных окончен')
            print(self.count_page)
            # print(1)

    def parse_item(self, response:HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('name', '//div[@class="product-content"]//h1/text()')
        loader.add_xpath('photos', '//picture[@slot="pictures"]//img//@src')
        loader.add_xpath('parameter', '//dl//dt//text() | //dl//dd//text()')
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//uc-pdp-price-view[@class="primary-price"]//span/text()')
        loader.add_xpath('currency', '//uc-pdp-price-view[@class="primary-price"]//span[2]/text()')
        loader.add_xpath('dimension', '//uc-pdp-price-view[@class="primary-price"]//span[3]/text()')

        yield loader.load_item()
        # print(1)

