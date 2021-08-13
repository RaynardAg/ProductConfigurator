import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from re import sub

"""Generate a url from scratch"""
def get_url(search_term):

    template = 'https://www.amazon.com/s?k={}'
    search_term = search_term.replace(' ', '+')

    url = template.format(search_term)

    url += '&page={}'

    return url

"""Parse the html and extract the desired information"""
def extract_record(item):

    #description and url
    atag = item.h2.a
    description = atag.text.strip()
    produrl = 'https://www.amazon.com' + atag.get('href')

    try:
        #price
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
        price = float(sub(r'[^\d.]', '', price[1:]))

    except AttributeError:
        return

    try:
        #rating
        rating = item.i.find('span', 'a-icon-alt').text
        rating = float(rating[0:3])
        review_count = item.find('span', {'class': 'a-size-base'}).text
    except AttributeError:
        rating = ''
        review_count = ''

    result = [description, price, rating, review_count, produrl]

    return result

"""Main program routine"""
def main(search_term):

    #startup the webdriver
    driver = webdriver.Firefox()

    records = []
    url = get_url('3d printer')

    for page in range(1,21):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})

        for item in results:
            extractrec = extract_record(item)
            try:
                if extractrec[0] not in records and extractrec[1] > 99:
                    records.append(extractrec)
            except TypeError:
                continue
    driver.close()

    """ Store record in csv file """
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Description', 'Price', 'Rating', 'ReviewCount', 'Url'])
        writer.writerows(records)

""" Run main function"""
main('3d printer')