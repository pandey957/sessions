from bs4 import BeautifulSoup
from urllib import urlopen
from unicode import UnicodeWriter
import os
def writerecord(url,wrtr):
    data = BeautifulSoup(urlopen(url),"html.parser")
    #print url
    for item in data.findAll('div','card'):
        if (item.find('div','name') == None): break
        name = item.find('div','name').text.strip()
        place = item.find('div','place').text.strip()
        phone = item.find('a','mob-link').text.strip()
        if len(phone) == 0: continue
        wrtr.writerow([name,place,phone])

def locations(loc_file):
    data = BeautifulSoup(open(loc_file + '.html'),"html.parser")
    for line in data.find('div','filters_value_container').find('ul').findAll('li'):
        yield line.text.strip()

if __name__ == '__main__':    
    base_url = 'https://www.askme.com/search?q='
    outfile = open('askme_banglore.csv','w')
    wrtr = UnicodeWriter(outfile)
    loc = 'bangalore'
    for locality in locations(loc):
        url = base_url+'shops+'+locality.replace('.','').replace('-','').replace(' ','+')+'&type=outlets&city='+loc
        #print('writing for' + url)
        writerecord(url,wrtr)
    #writerecord(base_url,wrtr)
    outfile.close()
