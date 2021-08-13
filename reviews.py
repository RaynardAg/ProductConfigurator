import csv
from bs4 import BeautifulSoup
from selenium import webdriver

""" Extract information from previous web scraping stage"""
def get_url(csv_name):

    with open(csv_name + '.csv', encoding='UTF-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        urllist = []
        next(csv_reader)
        for row in csv_reader:
            urllist.append(row[5])
    return urllist

"""Get the urls for the user reviews of each product"""
def extract_reviewurl(item):

    revlinks = []
    revurl = item.find('a', {"class" : "a-link-emphasis"})
    reviewurl = revurl.get('href')
    reviewurl = 'https://www.amazon.com' + reviewurl + '&pageNumber={}'
    revlinks.append(reviewurl)

    return revlinks

"""Extract the user reviews"""
def extract_reviews(item):

    #review text
    revtext = item.find('span', {'class' : 'a-size-base review-text review-text-content'}).text
    revtext = revtext.strip()

    results = revtext
    return results

"""Main program routine"""
def main(filename):
    # startup the webdriver
    driver = webdriver.Chrome()

    revlinks = []
    onerev = []
    urllinks = get_url(filename)
    reviews = []
    reviewcount = []

    # Extract the urls of the user reviews of each product
    for item in urllinks:
        driver.get(item)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find('div', {'class': 'a-fixed-right-grid-col cm_cr_grid_center_right'})
        try:
            revlinks = extract_reviewurl(results)
        except AttributeError:
            reviews.append('No customer reviews')

        # Extract the user reviews for each product from the user reviews page
        for x in revlinks:
            revcount = 0
            for page in range(1, 6):
                print(x.format(page))
                driver.get(x.format(page))
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                finds = soup.find_all('div', {'class': 'a-section celwidget'})
                # Extract the information from each user review
                for q in finds:
                    revcount += 1
                    print(revcount)
                    extractrev = extract_reviews(q)
                    if extractrev:
                        onerev.append(extractrev)
                reviews.append(onerev)
                onerev = []
            reviewcount.append(revcount)
            print(len(reviewcount))
        revlinks = []
    driver.close()

    """Add information to the previous CSV file with the new extracted information"""
    with open('details.csv', 'r', encoding='utf-8') as read_obj, \
            open('reviews.csv', 'w', newline='', encoding='utf-8') as write_obj:
        reader = csv.reader(read_obj)
        writer = csv.writer(write_obj)
        idx = 0
        for row in reader:
            num = len(row)-1
            if row[0] == "Title":
                writer.writerow(row + ["Number of Reviews"] + ["Reviews"])
            else:
                for x in range(0,num):
                    if len(row) == 6:
                        row.append(reviewcount[idx])
                        row.append(reviews[idx])
                        idx +=1
                        print(row)
                    elif idx == num:
                        pass
                    else:
                        pass
            writer.writerow(row)

"""Run main function"""
main('details')