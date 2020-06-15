import requests
from bs4 import BeautifulSoup
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config

from config import owmToken

config_dict = get_default_config()
config_dict['language'] = 'EN'


def day_weather(city):
    owm = OWM(owmToken, config_dict)

    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(city)
    w = observation.weather

    curr_weather = [int(w.temperature('celsius')['temp_min']), int(w.temperature('celsius')['temp_max']),
                    int(w.temperature('celsius')['temp']), w.detailed_status]
    return curr_weather


def get_article():
    bbc_request = requests.get('https://www.bbc.com/news')
    soup = BeautifulSoup(bbc_request.text, "html.parser")
    raw_article = soup.find_all('div', {'class': 'gs-c-promo-body gel-1/2@xs gel-1/1@m gs-u-mt@m'})[0].find_all(
        text=True, recursive=True)
    if raw_article[0].startswith(
            'Video'):
        topic = raw_article[5]
        title = raw_article[1]
        description = raw_article[2]
        publish_time = raw_article[4]
    else:
        topic = raw_article[4]
        title = raw_article[0]
        description = raw_article[1]
        publish_time = raw_article[3]
    href = soup.find_all('div', {'class': 'gs-c-promo-body gel-1/2@xs gel-1/1@m gs-u-mt@m'})[0].find('a', {
        'class': 'gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor'})['href']
    link = f' https://www.bbc.com{href}'
    article = f'<b>Category</b>: {topic}\n<b>Headline</b>: {title}\n<b>Short description</b>: ' \
              f'{description}\n<b>Time has passed' \
              f'</b>: {publish_time} '
    return article
