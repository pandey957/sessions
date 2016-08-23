from bs4 import BeautifulSoup
from urllib import urlopen
import csv
from unicode import UnicodeWriter, UnicodeReader
import os
def writerecord(url,wrtr,category='shops'):
    data = BeautifulSoup(urlopen(url),"html.parser")
    #print url
    for item in data.findAll('div','card'):
        if (item.find('div','name') == None): break
        name = item.find('div','name').text.strip()
        place = item.find('div','place').text.strip()
        phone = item.find('a','mob-link').text.strip()
        if len(phone) == 0: continue
        wrtr.writerow([category,name,place,phone])

def locations(city_file):
    in_file = open(city_file)
    reader = csv.reader(in_file)
    for line in reader:
        yield (line[0], line[1])


if __name__ == '__main__':
    base_url = 'https://www.askme.com/search?q='
    outfile = open('askme_mumbai.csv','w')
    categories = map(lambda x: x.strip(),open('categories').readlines())
    wrtr = UnicodeWriter(outfile)
    wrtr.writerow(['category','name','address','phone'])
    for locality,city in locations('mumbai_localities.csv'):
        loc = locality.replace('.','').replace('-','').replace(' ','+')
        for category in categories:
            cat = category.strip().replace(' ','+') + '+'
            url = base_url+cat+'in+'+loc+'&type=outlets&city='+city
            writerecord(url,wrtr,category)
    outfile.close()
