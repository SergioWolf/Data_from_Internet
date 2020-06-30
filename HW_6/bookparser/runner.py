from scrapy.crawler import CrawlerProcess           #Импортируем класс для создания процесса
from scrapy.settings import Settings                #Импортируем класс для настроек

from bookparser import settings                      #Наши настройки
from bookparser.spiders.book24ru import Book24ruSpider       #Класс паука
from bookparser.spiders.labirintru import LabirintruSpider     #Класс второго паука


if __name__ == '__main__':
    crawler_settings = Settings()                   #Создаем объект с настройками
    crawler_settings.setmodule(settings)            #Привязываем к нашим настройкам

    process = CrawlerProcess(settings=crawler_settings)     #Создаем объект процесса для работы
    process.crawl(Book24ruSpider)                               #Добавляем нашего паука
    process.crawl(LabirintruSpider)

    process.start()