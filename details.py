import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from re import sub

""" Extract information from previous web scraping stage"""
def get_url(csv_name):

    with open(csv_name + '.csv', encoding='UTF-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        urllist = []
        next(csv_reader)
        for row in csv_reader:
            urllist.append(row[4])
    return urllist

"""Parse the html and extract the desired information"""
def extract_record(item):

    try:
        #title
        title = item.find('span', id="productTitle").text
        title = title.strip()
    except AttributeError:
        return

    #features
    try:
        features=[]
        features = item.find("ul", {"class" : "a-unordered-list a-vertical a-spacing-mini"}).text
        features = features.splitlines()
        while '' in features:
            features.remove('')
        features = features[3:]
    except AttributeError:
        features.append('')

    try:
        #price
        price = item.find('span', {"class" : "a-size-medium a-color-price"}).text
        price = round(float(sub(r'[^\d.]', '', price[1:])))
    except (TypeError,ValueError,AttributeError) as e:
        return

    try:
        #rating
        rating = item.find('span', {"class" : "a-icon-alt"}).text
        rating = float(rating[0:3])
    except AttributeError:
        rating = ''

    try:
        #review count
        review_count = item.find("span", id="acrCustomerReviewText").text
    except AttributeError:
        review_count = ''

    result = [title, price, features, rating, review_count]

    return result

"""Main program routine"""
def main(filename):

    # startup the webdriver
    driver = webdriver.Firefox()

    details = []
    urllinks = get_url(filename)

    for item in urllinks:
        driver.get(item)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find('div', {'id': 'ppd'})
        res = extract_record(results)
        try:
            res2 = []
            res2 += res
            res2.append(item)
            details.append(res2)
            print(len(details))
        except TypeError:
            pass
    driver.close()

    """ Store record in csv file """
    with open('details.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Price', 'Features', 'Rating', 'ReviewCount', 'Url'])
        writer.writerows(details)

""" Run main function"""
main('results')
