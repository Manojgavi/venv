import re
import requests
import csv
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse


class MultiThreadScraper:

    def __init__(self, q):

        self.base_url = "http://google.com/search?q="
        self.q = q + ' Departments'
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=8)
        self.scraped_pages = set([])
        self.to_crawl = Queue()
        self.to_crawl.put(self.base_url)
        self.emails = set([])

    def parse_links(self, html):
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
                if url not in self.scraped_pages:
                    if not url.endswith(".pdf"):
                        self.to_crawl.put(url)

    def scrape_info(self, html):
        soup = BeautifulSoup(html)
        new_emails = soup.find_all('a', href=True)
        for link in new_emails:
            if "http" in link['href'] and "maps" not in link['href']:
                print(link['href'])
                res = link['href']
                res2=res[res.find('http'):]
                found = res2[:res2.find("&")]
                print(found)
                break
        self.emails.update([found])
        return

    def post_scrape_callback(self, res):
        result = res.result()
        #if result and result.status_code == 200:
            #self.parse_links(result.text)
        self.scrape_info(result.text)

    def scrape_page(self, base_url):
        try:
            headers_Get = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            se = requests.Session()

            q = self.q
            print(q)
            base_url += '+'.join(q.split())
            url = base_url + '&ie=utf-8&oe=utf-8'
            r = se.get(url, headers=headers_Get)
            print(url)
            print(r);


            return r
        except requests.RequestException:
            print('timeout')
            return

    def run_scraper(self):
        while True:
            try:
                target_url = self.to_crawl.get(timeout=0)
                if target_url not in self.scraped_pages:
                    print("Scraping URL: {}".format(target_url))
                    self.scraped_pages.add(target_url)
                    job = self.pool.submit(self.scrape_page, target_url)
                    job.add_done_callback(self.post_scrape_callback)
            except Empty:

                return
            except Exception as e:
                print(e)
                continue


class Scraper:

    def __init__(self, file):

        self.input_file = file
        self.pages = []

    def read_file(self):
        print('Reading File')
        with open(self.input_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\n')
            for row in reader:
                print(row)
                self.pages.append(row)

    def run_scrape(self):
        for page in self.pages:
            writer = csv.writer(open("output1-250.csv", 'a'))
            print('-----Scraping page: ' + page[0])
            s = MultiThreadScraper(page[0])
            s.run_scraper()
            writer.writerow(s.emails)
            print("Completed " + page[0])


if __name__ == '__main__':
    s = Scraper('universitynames.csv')
    s.read_file()
    s.run_scrape()


