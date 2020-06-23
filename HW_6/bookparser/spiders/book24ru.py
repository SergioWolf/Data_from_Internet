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


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    main_url = 'https://book24.ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5']

    count_page = 0

    def parse(self, response:HtmlResponse):

        next_page = response.css('button.js-pagination-catalog-item::attr(data-href)').extract_first()
        next_page_link = self.main_url + next_page
        books_links = response.css('div.catalog-products__list a.book__title-link::attr(href)').extract()
        for link in books_links:
            link_book = self.main_url + link
            yield response.follow(link_book, callback=self.book_parce)

        self.count_page += 1
        print(self.count_page)
        yield response.follow(next_page_link, callback=self.parse)


    def book_parce(self, response: HtmlResponse):
        link_book = response.url
        name_book = response.xpath('//h1/text()').extract_first()
        author_book = response.xpath('//div[@class="item-tab__chars-item"][1]//span/a/text()').extract()
        price = response.xpath('//div[@class="item-actions__price"]//b/text()').extract_first()
        priceold = response.xpath('//div[@class="item-actions__price-old"]/text()').extract_first()
        rating_book = response.css('div.rating__value-box span.rating__rate-value::text').extract_first()
        yield BookparserItem(link=link_book, name=name_book, author=author_book, price_basic=priceold, price_discount=price,
                             rating=rating_book)
        #print(name_book, author_book, price, priceold, rating_book)
        #print(1)

