from bs4 import BeautifulSoup
import urllib.request as lib
import csv
import os
import re

# url -> URL pointing to the first page of the company's reviews
# fileName -> name of file data will be saved to (file does not need to already exist)
def scrapeCompanyReviews(url, fileName):

    # list of reviews
    text = []
    header = []
    job_title = []
    currentFormer = []
    location = []
    date = []
    stars = []

    # whether to go to next page of reviews
    bool = True
    # current index of review
    start = 0

    while(bool):

        # get HTML
        req = lib.Request(url + '?start=' + str(start), headers={'User-Agent': 'Mozilla/5.0'})
        webpage = lib.urlopen(req)
        soup = BeautifulSoup(webpage, 'html.parser')

        # find reviews
        current_text = soup.find_all('span', attrs={'class' : 'cmp-review-text', 'itemprop' : 'reviewBody'})
        current_header = soup.find_all('div', attrs={'class': 'cmp-review-title'})
        current_job_title = soup.find_all('span', attrs={'class': 'cmp-reviewer'})
        current_location = soup.find_all('span', attrs={'class': 'cmp-reviewer-job-location'})
        if(len(current_location) != len(current_header)):
            if(len(current_header) == 21):
                start+=20
                continue
            else:
                bool = False
                continue
        current_date = soup.find_all('span', attrs={'class': 'cmp-review-date-created'})
        current_stars1 = soup.find_all('span', attrs={'class': 'cmp-Rating-on'})
        if(len(current_stars1) == 127):
            continue
        current_stars2 = [current_stars1[i] for i in range(len(current_stars1)) if i%6==1][:-1]
        current_stars = [str(int(i['style'][7:-4])/20) for i in current_stars2]
        current_currentFormer = soup.find_all('span', attrs={'class': 'cmp-reviewer-job-title'})
        current_currentFormer = [re.search('\(([^)]+)', i.text).group(1) for i in current_currentFormer]
        current_currentFormer = [int(i == 'Current Employee') for i in current_currentFormer]

        if(len(current_text) != len(current_stars) != len(current_location)):
            print(start)
            print([i.text.strip()[:10] for i in current_text])
            print(len(current_stars1))
            print(len(current_stars2))
            print(current_stars)
            print(current_location)

        if(len(current_text) != 21):
            bool = False

        # if second or more page, remove first review
        if(start != 0 and len(current_text) != 0):
            current_text.pop(0)
            current_header.pop(0)
            current_job_title.pop(0)
            current_location.pop(0)
            current_date.pop(0)
            current_stars.pop(0)
            current_currentFormer.pop(0)

        if (len(current_text) != len(current_stars) != len(current_location)):
            print(start)
            print([i.text.strip()[:10] for i in current_text])
            print(current_stars)
            print(current_location)

        # index to next page
        start += 20

        # add text to list
        for i in current_text:
            text.append(i.text.strip().encode('ascii', errors='ignore').decode())

        # add headers to list
        for i in current_header:
            header.append(i.text.strip().encode('ascii', errors='ignore').decode())

        # add job titles to list
        for i in current_job_title:
            job_title.append(i.text.strip().encode('ascii', errors='ignore').decode())

        # add locations to list
        for i in current_location:
            location.append(i.text.strip().encode('ascii', errors='ignore').decode())

        # add dates to list
        for i in current_date:
            date.append(i.text.strip().encode('ascii', errors='ignore').decode())

        # add stars to list
        for i in current_stars:
            stars.append(i)

        # add stars to list
        for i in current_currentFormer:
            currentFormer.append(i)

    with open(fileName, 'a', newline = '') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["company", "date", "job_title", "CurrentEmployee", "location", "header", "text", "stars"])
        print(len(date), len(job_title), len(currentFormer), len(location), len(header), len(text), len(stars))
        for i, v in enumerate(text):
            writer.writerow([re.search('cmp/(.*)/', url).group(1), date[i], job_title[i],
                             currentFormer[i], location[i], header[i], text[i], stars[i]])


# companyURLs -> list of URL's, one for each company to be scraped (url must point to first page of reviews)
# fileName -> name of file data will be saved to (file doesn't need to already exist)
def scrapeMultipleCompaniesReviews(companyURLs, fileName):
    if(os.path.isfile('indeed-com.csv')):
        os.remove('indeed-com.csv')

    [getData(i, fileName) for i in urls]