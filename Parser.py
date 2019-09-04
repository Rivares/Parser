import re
import csv

import requests
from bs4 import BeautifulSoup

countBoxes = '3'
typeBoxes = 'novostroyka'

def get_html(url):
    r = requests.get(url)
    return r.text


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find('div', class_='pagination-pages clearfix')
    pages = divs.find_all('a', class_='pagination-page')[-1].get('href')
    total_pages = pages.split('=')[1].split('&')[0]
    return int(total_pages)


def write_csv(data):
    with open('avito.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow((data['mark'],
                         data['space'],
                         data['level'],
                         data['price'],
                         data['km'],
                         data['url']))

def sort(flat):
    markForSpace = 0
    markForLevel = 0
    markForPrice = 0
    markForKm = 0

    # Borders
    borderSpace = (40, 90)
    borderLevel = (0, 9)
    borderPrice = (3500000, 8000000)
    borderKm = (0, 5)

    scale = (1, 10)

    stepSpace = (scale[1] - scale[0]) / (borderSpace[1] - borderSpace[0])
    stepLevel = (scale[1] - scale[0]) / (borderLevel[1] - borderLevel[0])
    stepPrice = (scale[1] - scale[0]) / (borderPrice[1] - borderPrice[0])
    stepKm = (scale[1] - scale[0]) / (borderKm[1] - borderKm[0])

    scaledSpace = []
    scaledLevel = []
    scaledPrice = []
    scaledKm = []

    i = scale[0]
    while i <= scale[1]:
        scaledSpace.append(i)
        i = i + stepSpace

    i = scale[0]
    while i <= scale[1]:
        scaledLevel.append(i)
        i = i + stepLevel

    i = scale[0]
    while i <= scale[1]:
        scaledPrice.append(i)
        i = i + stepPrice

    i = scale[0]
    while i <= scale[1]:
        scaledKm.append(i)
        i = i + stepKm

    if (flat[0] < borderSpace[0]) or (flat[0] > borderSpace[1]) or \
        (flat[1] <= borderLevel[0]) or (flat[1] > borderLevel[1]) or \
        (flat[2] <= borderPrice[0]) or (flat[2] > borderPrice[1]) or \
        (flat[3] <= borderKm[0]) or (flat[3] > borderKm[1]):

        """ 40..90 m2
            2..5 l
            3500000..9000000 $
            0..5 km and m
        """
        markForSpace = 0
        markForLevel = 0
        markForPrice = 0
        markForKm = 0
    else:
        # print("Input = ", flat[0], ", ", flat[1], ", ", flat[2], ", ", flat[3])
        # print("Size = ", len(scaledSpace), ", ", len(scaledLevel), ", ", len(scaledPrice), ", ", len(scaledKm))
        # print("Space = ", scaledSpace)
        # print("Level = ", scaledLevel)

        # Space
        for i in range(borderSpace[0], borderSpace[1]):
            if i > flat[0]:
                # print("Need index: ", i - borderSpace[0])
                markForSpace = scaledSpace[i - borderSpace[0]]
                break

        # print("markForSpace = ", markForSpace)

        # Level
        for i in range(borderLevel[0], borderLevel[1]):
            if i > flat[1]:
                # print("Need index: ", i - borderLevel[0])
                markForLevel = scaledLevel[i - borderLevel[0]] + 1
                break

        # print("markForLevel = ", markForLevel)

        # Price

        for i in range(borderPrice[0], borderPrice[1]):
            if i > flat[2]:
                # print("Need index: ", i - borderPrice[0])
                markForPrice = scaledPrice[len(scaledPrice) - 1] - scaledPrice[i - borderPrice[0]]
                break

        # print("markForPrice = ", markForPrice)

        # Km
        for i in range(borderKm[0], borderKm[1]):
            if i > flat[3]:
                # print("Need index: ", i - borderKm[0])
                markForKm = scaledKm[len(scaledKm) - 1] - scaledKm[i - borderKm[0]]
                break

        # print("markForKm = ", markForKm)

        generalMark = markForSpace + markForLevel + markForPrice + markForKm
        flatToTable = {'mark': str(generalMark), 'space': str(flat[0]), 'level': str(flat[1]), 'price': str(flat[2]), 'km': str(flat[3]), 'url': str(flat[4])}
        write_csv(flatToTable)

        # print("Mark the flat: ", markForSpace, ", ", markForLevel, ", ", markForPrice, ", ", markForKm)
        # print("Sum of all marks: ", generalMark)



def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find('div', class_='catalog-list')

    ads = divs.find_all('div', class_='item_table')

    for ad in ads:
        try:
            div = ad.find('div', class_ ='description').find('h3')
            if (countBoxes + '-к квартира') not in div.text.lower():
                continue
            else:
                title = div.text.strip()
                title = title.strip(countBoxes + '-к квартира' + ', ')
                searchObj = re.search(r'(.*) м², (.*?) .*', title, re.M | re.I)

                space = searchObj.group(1)

                searchObj = re.search(r'.*/', searchObj.group(2), re.M | re.I)
                level = searchObj.group().strip('/')

                level = level

                # print(space)
                # print(level)
        except:
                space = ''
                level = ''
                title = ''
        try:
            div = ad.find('div', class_='description').find('h3')
            url = "https://avito.ru" + div.find('a').get('href')
        except:
            url = ''
        try:
            price = ad.find('div', class_='about').text.strip()
        except:
            price = ''
        try:
            div = ad.find('p', class_='address')
            km = div.find('span', class_='c-2').text.strip()
        except:
            metro = ''

        # print("get_page_data: space =",  space, ";level =", level, ";price = ", price, ";km = ", km, ";url = ", url)

        if isinstance(space, str):
            if space.find('.') != 0:
                space = float(space)
                space = int(space)

        if isinstance(level, str):
            level = int(level)

        if isinstance(price, str):
            price = price.replace(' ', '')
            price = price.strip('₽')
            price = int(price)

        if isinstance(km, str):
            km = km.strip(' км')
            if km.find(' м') == 0:
                km = int('1')
            else:
                if km.find('.') != 0:
                    km = float(km)
                    km = int(km)

        dataForSort = (space, level, price, km, url)
        sort(dataForSort)

def main():
    url = "https://www.avito.ru/sankt-peterburg/kvartiry/prodam/" + countBoxes + "-komnatnye/" + typeBoxes
    base_url = "https://www.avito.ru/sankt-peterburg/kvartiry/prodam/" + countBoxes + "-komnatnye/" + typeBoxes + "?"
    page_part = "p="
    query_par = "&f=59_13989b?"

    # total_pages = get_total_pages(get_html(url))

    for i in range(1, 5):       # 8 is maximum
        url_gen = base_url + page_part + str(i) + query_par
        html = get_html(url_gen)
        get_page_data(html)


if __name__ == '__main__':
    main()
