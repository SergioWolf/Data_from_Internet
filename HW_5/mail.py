# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные
# о письмах в базу данных: от кого, дата отправки, тема письма, текст письма полный
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172
import time
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import unicodedata

from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options

MONGO_URI = 'mongodb://127.0.0.1:27017/'
MONGO_DATABASE = 'mail_db'

client = MongoClient(MONGO_URI)
mongo_base = client[MONGO_DATABASE]
collection = mongo_base['letters']

chrome_options = Options()
#chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome()

driver.get('https://www.mail.ru')
assert 'Mail.ru: почта, поиск в интернете, новости, игры' in driver.title

login = driver.find_element_by_id('mailbox:login')
login.click()
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.RETURN)

time.sleep(1)

paswd = driver.find_element_by_id('mailbox:password')
paswd.click()
paswd.send_keys('NextPassword172')
paswd.send_keys(Keys.RETURN)

time.sleep(10)

driver.get('https://m.mail.ru/inbox/')
# Как избежать "костылей" из временных задержек и дополнительного get запроса??? Но даже с ними
# С обычной версии сайта ни какими методами не получается выдернуть ссылку на первое письмо,
# почему осталось большим вопросом???
# после команды print(driver.page_source) выходил код стартовой страницы, а не с входящими письмами???


WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'msglist')))
letter_link = driver.find_element(By.CSS_SELECTOR, 'table.msglist a.messageline__link').get_attribute('href')

def scrap_letter(page: str):

        driver.get(page)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'footer')))
        data = {
            'url': driver.current_url,
            'header': driver.find_element(By.CSS_SELECTOR, 'span.readmsg__theme').text.replace('\n', '').replace('\t', ''),
            'sender': driver.find_element(By.CSS_SELECTOR, 'span.readmsg__addressed-word ~ a').text,
            'date': driver.find_element(By.CSS_SELECTOR, 'span.readmsg__mail-date').text,
            'text': unicodedata.normalize('NFKD', driver.find_element(By.ID, 'readmsg__body').text).replace('\n', ' ')
                .replace('\t', ' ').replace('  ', ''),
        }

        return data

count = 0
while True:
    try:
        letter = scrap_letter(letter_link)
        count += 1
        print(count)
        collection.update_one({'_id': letter['url']}, {'$set': letter}, upsert=True)

        next_link = driver.find_element(By.CSS_SELECTOR,
                    'div.readmsg__horizontal-block__right-block > a.readmsg__text-link')
        if (next_link):
            letter_link = next_link.get_attribute('href')

    except exceptions.NoSuchElementException:
        print('Сбор входящих писем окончен')
        break

print(f'Количество обработанных писем: {count}')
pprint(letter)

driver.close()



