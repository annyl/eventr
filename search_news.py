import vk_requests
import re
from transliterate import translit
from datetime import datetime
import requests
from xml.etree import ElementTree as ET


class Eventr(object):

    FILTERS = ['ключевые слова', 'подборка']
    MONTHS = {'января': '01',
              'февраля': '02',
              'марта': '03',
              'апреля': '04',
              'мая': '05',
              'июня': '06',
              'июля': '07',
              'августа': '08',
              'сентября': '09',
              'октября': '10',
              'ноября': '11',
              'декабря': '12'}
    DAYS = {'сегодня': 0,
            'завтра': 1,
            'вчера': -1}

    TODAY = datetime.strftime(datetime.now(), "%m%d") #'1216' format

    def __init__(self, city='Нижний Новгород, Горьковская ул'):
        self.__api = vk_requests.create_api(app_id=YOUR_APP_ID,
                                            service_token='YOUR_SERVICE_TOKEN')
        self.__date_pattern = re.compile(r"((?:(?:(?:(?:\d+-)?\d+\s)(?:" + '|'.join(['(?:' + month + ')' for month in list(self.MONTHS) + list(self.DAYS)]) + r"))|(?:(?:\d{2}\.){2}\d+)|(?:<>)))")
        self.__snippet_pattern = ''
        response = requests.get(' http://geocode-maps.yandex.ru/1.x/', dict(geocode=city, results='1'))
        self.longitude, self.latitude = tuple([float(i) for i in ET.fromstring(response.text)[0][1][0][4][0].text.split()])

    def __transliteration(self, text=''):
        return [text, translit(text, 'ru', reversed=True), text.replace('-', ''), text.replace('-', ' '), ''.join(text.split())]

    def __has_date(self, text=''):
        return self.__date_pattern.findall(text)

    def __has_filter_words(self, text=''):
        return any(filter_word in text.lower() for filter_word in self.FILTERS)

    def __filter_times(self, post_dates, post_unix=0):
        post_date = post_dates[0]
        post_date_publish = datetime.fromtimestamp(post_unix).strftime("%m%d")
        if ' ' in post_date:
            post_date_digital = self.MONTHS[re.findall('[а-я]+', post_date)[0]] + re.findall('\d+', post_date)[0] if len(re.findall('\d+', post_date)[0]) == 2 else '0' + re.findall('\d+', post_date)[0]
        else:
            if post_date in list(self.DAYS):
                post_date_digital = str(int(post_date_publish) + self.DAYS[post_date])
            else:
                post_date_digital = re.findall('\d+', post_date)[1] + re.findall('\d+', post_date)[0]
        if post_date_digital >= self.TODAY:
            return post_date_digital[2:] + '/' + post_date_digital[:2]
        else:
            return False

    def get_news(self, query, offset='', filtered=True):
        try:
            news_raw = self.__api.newsfeed.search(q=query, extended=False, count=200, latitude=self.latitude, longitude=self.longitude, start_from=offset) #start_time=int(datetime.now().timestamp()) - 604800
            if filtered:
                return list(sorted([{'link': 'https://vk.com/wall' + str(item['owner_id']) + '_' + str(item['id']), 'date': self.__filter_times(self.__has_date(item['text'])), 'snippet': item['text'] if len(item['text']) <= 500 else item['text'][:500]}
                        for item in news_raw['items'] if not self.__has_filter_words(item['text'])
                            and self.__has_date(item['text'])
                            and item['owner_id'] < 0
                            and self.__filter_times(post_dates=self.__has_date(item['text']), post_unix=item['date'])], key=lambda x: x['date'])) + self.get_news(query, offset=news_raw['next_from'], filtered=filtered)
            else:
                return [item['text'] for item in news_raw['items']] + self.get_news(query, offset=news_raw['next_from'], filtered=filtered)
        except KeyError:
            return []


def main():
    eventr = Eventr()
    for text in eventr.get_news(query='выставка', filtered=True):
        print(text)


if __name__ == '__main__':
    main()
