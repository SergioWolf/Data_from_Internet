# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from instagrampars.items import InstagramparsItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'sergwolf3'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:9:1593425157:AVdQAAvAOJkB8D1EcVQjsx8+PDnfOM8Z7jCdhpsIIVjeHaFAxPxi3xX4BnL+4/d9bjRavgl205AjUgQiCT0Y9eUBPhG65uTRYTni+jPMtXUEQomIeU4SIAFrLa3GSseq6swVt0gqoUHM3lOsZJVp'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = ['dominicana.pro', 'hola_mexico_cancun']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    subscriber_hash = 'c76146de99bb02f6415203be841dd25a'
    subscription_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response:HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:                 #Проверяем ответ после авторизации
            for i in  range(len(self.parse_user)):
                yield response.follow(                  #Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                    f'/{self.parse_user[i]}',
                    callback= self.user_data_parse,
                    cb_kwargs={'username': self.parse_user[i]}
                )

    def user_data_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       #Получаем id пользователя
        variables={'id': user_id,                                    #Формируем словарь для передачи даных в запрос
                   'first': 12}                                      #12 постов. Можно больше (макс. 50)
        url_subscriber = f'{self.graphql_url}query_hash={self.subscriber_hash}&{urlencode(variables)}'    #Формируем ссылку для получения данных о постах
        url_subscription = f'{self.graphql_url}query_hash={self.subscription_hash}&{urlencode(variables)}'
        yield response.follow(
            url_subscriber,
            callback=self.user_subscriber_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}         #variables ч/з deepcopy во избежание гонок
        )
        yield response.follow(
            url_subscription,
            callback=self.user_subscription_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

    def user_subscriber_parse(self, response:HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_subscriber = f'{self.graphql_url}query_hash={self.subscriber_hash}&{urlencode(variables)}'
            yield response.follow(
                url_subscriber,
                callback=self.user_subscriber_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        subscribers = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for subscriber in subscribers:
            item = InstagramparsItem(
                user_id = subscriber['node']['id'],
                username = subscriber['node']['username'],
                full_name = subscriber['node']['full_name'],
                user_photo = subscriber['node']['profile_pic_url'],
                user_attribute = 'subscriber',
                full_info = subscriber['node']
            )
        yield item

    def user_subscription_parse(self, response:HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_subscription = f'{self.graphql_url}query_hash={self.subscription_hash}&{urlencode(variables)}'
            yield response.follow(
                url_subscription,
                callback=self.user_subscription_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        subscriptions = j_data.get('data').get('user').get('edge_follow').get('edges')
        for subscription in subscriptions:
            item = InstagramparsItem(
                user_id = subscription['node']['id'],
                username = subscription['node']['username'],
                full_name = subscription['node']['full_name'],
                user_photo = subscription['node']['profile_pic_url'],
                user_attribute = 'subscription',
                full_info = subscription['node']
            )
        yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')