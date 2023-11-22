import requests
import lxml
from bs4 import BeautifulSoup as BS
from time import sleep
import json

base_url = 'https://online.metro-cc.ru'
headers = {"User-Agent":
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0"}

# Подсчет количества страниц
url = 'https://online.metro-cc.ru/category/bezalkogolnye-napitki/napitki-105003?in_stock=1'
response = requests.get(url, headers=headers)
soup = BS(response.text, "lxml")
number_of_pages = soup.find_all('a', class_="v-pagination__item catalog-paginate__item")[-1].text

base = {}  # Словарь в который будут записаны данные

for count in range(1, int(number_of_pages)+1):
    sleep(3)

    # Считывание элементов на текущей странице
    url = f'https://online.metro-cc.ru/category/bezalkogolnye-napitki/napitki-105003?in_stock=1&page={count}'
    response = requests.get(url, headers=headers)
    soup = BS(response.text, "lxml")
    class_ = 'catalog-2-level-product-card product-card subcategory-or-type__products-item with-rating with-prices-drop'
    data = soup.find_all('div', class_=class_)

    for item in data:
        # id
        pk = item.get('data-sku')

        base_item = {
            'id': pk.strip(),
            # Наименование товара
            'name': item.find('span', class_="product-card-name__text").text.replace('\n', '').lstrip().rstrip()
        }

        # Промо-цена
        promo_price_field = item.find('div', class_='product-unit-prices__actual-wrapper')
        promo_price = promo_price_field.find('span', class_='product-price__sum-rubles').text
        # Проверяем есть ли копейки в цене
        if promo_price_field.find('span', class_='product-price__sum-penny') is not None:
            promo_price += promo_price_field.find('span', class_='product-price__sum-penny').text

        # Регулярная цена
        price_field = item.find('div', class_="product-unit-prices__old-wrapper")
        price = price_field.find('span', class_='product-price__sum-rubles')
        # Здесь также проверяется есть ли копейки в цене, а также есть ли промо-акция на товар
        # В поле которое считывается выше, в разделе Промо-цена, попадает либо Промо-цена (если она существует)
        # либо Регулярная цена (если нет Промо-цены), поле, которое рассматривается в этом разделе
        # заполняется Регулярной ценой (если Промо-цена существует) или остается пустой (если Промо-цены нет)
        if price_field.find('span', class_='product-price__sum-penny') is not None and price is not None:
            price = price.text + price_field.find('span', class_='product-price__sum-penny').text
        elif price is not None:
            price = price.text
        else:  # Случай без промо-акции
            price, promo_price = promo_price, 'No promo'

        # Ссылка на товар
        href = base_url + item.find('a', class_="product-card-photo__link reset-link").get('href')

        base_item['url'] = href.strip()
        base_item['price'] = price.strip().replace(u"\u00A0", "")
        base_item['promo_price'] = promo_price.strip().replace(u"\u00A0", "")

        base[pk] = base_item

print(len(base))

for item in base:
    # Добавляем к записям название бренда
    sleep(3)
    href = base[item]['url']
    response = requests.get(href, headers=headers)
    soup = BS(response.text, 'lxml')
    base[item]['brand'] = soup.find('span',
                                    class_="product-attributes__list-item-value"
                                    ).text.replace('\n', '').lstrip().rstrip()

with open('result.json', 'w', encoding='utf-8') as output:
    json.dump(base, output, ensure_ascii=False)
