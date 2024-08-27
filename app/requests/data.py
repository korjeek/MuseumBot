from requests import Session
from bs4 import BeautifulSoup

session = Session()


async def get_museum_data(name, category, url):
    response = session.get(url)
    root = BeautifulSoup(response.text, 'lxml')
    description = root.find('div', class_='xZmPc').find_all(['p', 'div'])
    location = root.find('a', class_='K3Yd6').text.removeprefix('Свердловская обл., г. Екатеринбург, ')
    image = root.find('span', class_='A87lA WgrXI _0cLnb gA4Eg').find('img')

    result = (f'<b>{name}</b>\n\n'
              f'<b>Категория:</b> {category}\n'
              f'<b>Расположение:</b> {location}\n\n'
              f'<b>Описание:</b>\n'
              f'<a href="https://www.culture.ru' + image['src'] + '">&#8205;</a>')

    for paragraph in description:
        result += f'{paragraph.text}\n\n'

    return result
