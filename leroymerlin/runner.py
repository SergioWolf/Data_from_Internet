# 1) Взять любую категорию товаров на сайте Леруа Мерлен. Собрать с использованием ItemLoader следующие данные:
# - название;
# - все фото;
# - параметры товара в объявлении;
# - ссылка;
# - цена.
#
# С использованием output_processor и input_processor реализовать очистку и преобразование данных.
# Цены должны быть в виде числового значения.
#
# 2)Написать универсальный обработчик параметров объявлений, который будет формировать данные
# вне зависимости от их типа и количества.
#
# 3)*Реализовать хранение скачиваемых файлов в отдельных папках, каждая из которых должна соответствовать
# собираемому товару

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlin.spiders.leroymerlinru import LeroymerlinruSpider
from leroymerlin import settings

#ввод количества категорий товаров и их наименование
#здесь же осуществлять необходимо проверку корректности ввода, но пока без нее
def getInput():

    lst = []
    count = int(input("Введите количество категорий товаров: "))
    for i in range(count):
        lst.append(input("Ввведите название" + str(i+1) + "-ого товара: "))

    return lst

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider, sections=getInput())  #Передаем список параметров для поиска
    process.start()