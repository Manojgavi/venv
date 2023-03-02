import re
import requests
import csv
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse


class MultiThreadScraper:

    def __init__(self, base_url):

        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        print(self.base_url)
        print(self.root_url)
        self.pool = ThreadPoolExecutor(max_workers=8)
        self.scraped_pages = set([])
        self.to_crawl = Queue()
        self.to_crawl.put(self.base_url)
        self.emails = set([])

    def parse_links(self, html):
        soup = BeautifulSoup(html)
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
                if url not in self.scraped_pages:
                    if not url.endswith(".pdf") and "news" not in url and "video" not in url:
                        self.to_crawl.put(url)

    def scrape_info(self, html):
        new_emails = set(re.findall(r"([a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z0-9\.\-+_]+)",
                                    html, re.I))
        self.emails.update(new_emails)
        return

    def post_scrape_callback(self, res):
        result = res.result()
        if result and result.status_code == 200:
            self.parse_links(result.text)
            self.scrape_info(result.text)

    def scrape_page(self, url):
        try:
            url = url
            print(url)
            print(url[url.find("http"):])
            res = requests.get(url[url.find("http"):], timeout=(3, 30))
            return res
        except requests.RequestException:

            print('timeout')
            return

    def run_scraper(self):
        while True:
            try:
                target_url = self.to_crawl.get(timeout=60)
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
                self.pages.append(row)

    def run_scrape(self):
        for page in self.pages:
            writer = csv.writer(open("outputnew.csv", 'a'))
            print('-----Scraping page: ' + page[0])
            s = MultiThreadScraper(page[0])
            s.run_scraper()
            writer.writerow(s.emails)
            print("Completed " + page[0])


if __name__ == '__main__':
    s = Scraper('2.csv')
    s.read_file()
    s.run_scrape()
