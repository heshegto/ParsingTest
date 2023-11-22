import requests
import lxml
from bs4 import BeautifulSoup as BS

base_url = 'https://online.metro-cc.ru'

url = 'https://online.metro-cc.ru/category/bezalkogolnye-napitki/napitki-105003?in_stock=1&page=1'
response = requests.get(url)

soup = BS(response.text, "lxml")

data = soup.find('div',
                 class_='catalog-2-level-product-card product-card subcategory-or-type__products-item with-rating with-prices-drop')
pk_id = data.get('data-sku')
name = data.find('span', class_="product-card-name__text").text.replace('\n', '').lstrip().rstrip()

promo_price_field = data.find('div', class_='product-unit-prices__actual-wrapper')
promo_price = promo_price_field.find('span', class_='product-price__sum-rubles').text
if promo_price_field.find('span', class_='product-price__sum-penny') is not None:
    promo_price += promo_price_field.find('span', class_='product-price__sum-penny').text

price_field = data.find('div', class_="product-unit-prices__old-wrapper")
price = price_field.find('span', class_='product-price__sum-rubles')
if price_field.find('span', class_='product-price__sum-penny') is not None and price is not None:
    price = price.text + price_field.find('span', class_='product-price__sum-penny').text
elif price is not None:
    price = price.text
else:
    price, promo_price = promo_price, price
href = base_url + data.find('a', class_="product-card-photo__link reset-link").get('href')
response = requests.get(href)
soup = BS(response.text, 'lxml')
brand = soup.find('span', class_="product-attributes__list-item-value").text.replace('\n', '').lstrip().rstrip()

print(pk_id, name,href, price, promo_price, brand, sep='\n')
