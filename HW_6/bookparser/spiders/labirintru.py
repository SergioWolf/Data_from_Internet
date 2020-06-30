# -*- coding: utf-8 -*-
# 1) Создать двух пауков по сбору данных о книгах с сайтов labirint.ru и book24.ru
# 2) Каждый паук должен собирать:
# * Ссылку на книгу
# * Наименование книги
# * Автор(ы)
# * Основную цену
# * Цену со скидкой
# * Рейтинг книги
# 3) Собранная информация дожная складываться в базу данных

import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/']

    count_page = 0

    def parse(self, response:HtmlResponse):

        next_page = response.css('a.pagination-next__text::attr(href)').extract_first()
        if next_page != None:
            next_page_link = 'https://www.labirint.ru/search/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/' + next_page
            books_links = response.css('div.products-row a.product-title-link::attr(href)').extract()
            for link in books_links:
                link_book = 'https://www.labirint.ru' + link
                yield response.follow(link_book, callback=self.book_parce)
            self.count_page += 1

            yield response.follow(next_page_link, callback=self.parse)
        else:
            print('Сбор данных окончен')
            print(self.count_page)

    def book_parce(self, response:HtmlResponse):
        link_book = response.url
        name_book = response.xpath('//h1/text()').extract_first()
        author_book = response.xpath("//div[@class='authors']//a[@data-event-label='author']/text()").extract()
        price = response.xpath('//div[@class="buying-price"]//span[@class="buying-price-val"]//text()').extract_first()
        if price != None:
            priceold = price
            pricenew = None
        else:
            priceold = response.xpath('//div[@class="buying-priceold"]//span[@class="buying-priceold-val-number"]/text()').extract()
            pricenew = response.xpath('//div[@class="buying-pricenew"]//div[@class="buying-pricenew-val"]//text()').extract()
        rating_book = response.xpath('//div[@id="rate"]/text()').extract_first()
        yield BookparserItem(link=link_book, name=name_book, author=author_book, price_basic=priceold, price_discount=pricenew, rating=rating_book)

