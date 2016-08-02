from bs4 import BeautifulSoup
from urllib import urlopen
from unicode import UnicodeWriter

def insert_data(base_url, city, page = 1):
    url = base_url + str(page)
    data = BeautifulSoup(urlopen(url),'html.parser')
    for item in data.findAll('div','search-snippet-card'):
        #print item
        cateogry = None
        category_html = item.find('div','res-snippet-small-establishment')
        if category_html:
            category = category_html.text.replace(',','/')
        name = item.find('a','result-title').text.strip()
        phone = item.find('a','res-snippet-ph-info')['data-phone-no-str'].strip().replace(', ','/').replace(' ','-')
        address = item.find('div','search-result-address').text.strip()
        wrtr.writerow([city, category, name, phone, address])
    if data.find('a','next'):
        page += 1
        insert_data(base_url, city, page)


if __name__ == '__main__':
    url = 'https://www.zomato.com/pune/restaurants?credit-card=1&page='
    outfile = open('zomato.csv','wb')
    wrtr = UnicodeWriter(outfile)
    wrtr.writerow(['City, Category','Name', 'Phone', 'Address'])
    cities = ['ahmedabad','bangalore','chennai','hyderabad','mumbai','pune','kolkata','ncr']
    for city in cities:
        base_url = url.replace('pune',city)
        insert_data(base_url, city)
    outfile.close()
