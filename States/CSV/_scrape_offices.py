import requests
from bs4 import BeautifulSoup

import csv,codecs,cStringIO

class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
    def next(self):
        '''next() -> unicode
        This function reads and returns the next line as a Unicode string.
        '''
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        '''writerow(unicode) -> None
        This function takes a Unicode string and encodes it to the output.
        '''
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

states = ['az', 'ca', 'co', 'dc', 'fl', 'il', 'la', 'mi', 'mo', 'nv', 'nj',
          'or', 'pa', 'va', 'wa', 'wi']

for state in states:
    url = 'http://www.countyoffice.org/'+state+'-elections/'
    print "Scraping: " + url
    r = requests.get(url);
    scraped = BeautifulSoup(r.text, 'html.parser')
    table = scraped.find("div", class_="box-listings-2").find("table")
    links = table.find_all("td", class_="office-link")

    with open(state+'.csv', 'wb') as csv_file:
        csv_writer = UnicodeWriter(csv_file, delimiter=',')
        csv_writer.writerow(['name', 'address', 'city', 'state', 'zip',
                             'phone', 'fax'])

        
        for link in links:
            a = link.find("a").get("href")

            print " - Scraping: " + a
            
            r2 = requests.get('http://www.countyoffice.org/'+a);
            scraped2 = BeautifulSoup(r2.text, 'html.parser')
            dl = scraped2.find("dl", class_="LocalBusiness")

            name = dl.find("dd", class_="name").string
            address = dl.find("span", class_="streetAddress").string
            city = dl.find("span", class_="addressLocality").string
            state = dl.find("span", class_="addressRegion").string
            zip = dl.find("span", class_="postalCode").string
            phone = dl.find("dd", class_="telephone").string
            try:
                fax = dl.find("dd", class_="fax").string
            except:
                fax = ""

            csv_writer.writerow([name, address, city, state, zip, phone, fax])