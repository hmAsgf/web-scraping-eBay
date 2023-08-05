from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import os

def get_html(keyword: str, page: int):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    url = f'https://www.ebay.com/sch/i.html?_nkw={keyword}&_pgn={page}'
    res = requests.get(url, headers=headers)
    return res.text

def get_detail_product(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    content = BeautifulSoup(res.text, 'html.parser')
    return content.find('div', id='LeftSummaryPanel')

def parse_products(html, results):
    content = BeautifulSoup(html, 'html.parser')
    items = content.findAll('div', 's-item__image-section')
    items.pop(0)

    for item in items:
        image = item.find('div', 's-item__image-wrapper image-treatment').find('img')['src']
        link = item.find('a')['href']
        product = get_detail_product(link)

        if product:
            name = product.find('span', 'ux-textspans ux-textspans--BOLD').text
            condition = product.find('div', 'x-item-condition-text').find('span', 'ux-textspans').text
            price = product.find('div', 'x-price-primary').find('span', 'ux-textspans').text
            colors = ''
            sizes = ''

            location = product.find('div', 'ux-labels-values__values col-9').find('span', 'ux-textspans ux-textspans--SECONDARY')
            if location: location = location.text.replace('Located in: ', '')

            for i in range(2):
                option = product.find('select', id=f'x-msku__select-box-100{i}')
                if option:
                    option = product.find('select', id=f'x-msku__select-box-100{i}')['aria-label']
                    if 'Color' in option:
                        option = product.find('select', id=f'x-msku__select-box-100{i}').findAll('option')
                        color = [ops.text.replace('\xa0 (Out Of Stock)', '') for ops in option]
                        color.pop(0)
                        colors = ', '.join(color)

                    if 'Size' in option:
                        option = product.find('select', id=f'x-msku__select-box-100{i}').findAll('option')
                        size = [ops.text.replace('\xa0 (Out Of Stock)', '') for ops in option]
                        size.pop(0)
                        sizes = ', '.join(size)

            results.append({
                'Product Name': name,
                'Price': price,
                'Location': location,
                'Condition': condition,
                'Colors': colors,
                'Sizes': sizes,
                'Image': image,
                'Product Link': link
            })     
        time.sleep(1)

    return results

def to_csv(data):
    dataframe = pd.DataFrame(data)
    dataframe.to_csv('Data Products.csv', index=False)

def main():
    results = []
    for i in range(1, 4):
        html = get_html('shoes', i)
        results = parse_products(html, results)

    to_csv(results)

if __name__ == '__main__':
    main()