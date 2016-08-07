from bs4 import BeautifulSoup
from urllib import urlopen
from unicode import UnicodeWriter
import os

def writerecord(base_url,subcategory,city,page=1):
    url = base_url + '_' + str(page)
    data = BeautifulSoup(urlopen(url),'html.parser')
    for item in data.find('ol','list-group').findAll('li','list-item'):
        name = item.find('span',{'itemprop':'name'}).text
        info = item.find('div','item-info')
        phone_info = info.find('b','contact-number')
        if phone_info is None: continue
        phone = phone_info.text
        address = info.find('address').find('span').text
        wrtr.writerow([city,subcategory,name,phone,address])
        #print name, phone, address, city, subcategory
    if data.find('ul','pager'):
        if data.find('ul','pager').find('li','next'):
            page = page + 1
            writerecord(base_url, subcategory,city, page)


if __name__ == '__main__':
    base_url = 'http://yellowpages.sulekha.com/clothing-accessories_delhi_clistings'
    cities = ['chennai']
    outfile = open('chennai_sulekha1.csv','wb')
    wrtr = UnicodeWriter(outfile,delimiter=';')
    wrtr.writerow(['City','Category','Name','Phone','Address'])
    for city in cities:
        url = base_url.replace('delhi',city)
        next_iter = True
        links = BeautifulSoup(urlopen(url),'html.parser')
        for line in links.find('ol','business-clisting').findAll('div','blockTitle'):
            new_url = line.find('a')['href']
            if new_url == 'http://yellowpages.sulekha.com/tie-manufacturers_chennai':
                next_iter = False
            if next_iter: continue
            incity = '_' + city
            subcategory = new_url.split('/')[-1].replace('-',' ').replace(incity,'')
            writerecord(new_url,subcategory,city)
    outfile.close()
