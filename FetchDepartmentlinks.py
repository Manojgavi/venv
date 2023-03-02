from bs4 import BeautifulSoup
import requests
import csv

with open('univ1240-1500.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter='\n')
    for row in reader:
        print(row[0])
        writer = csv.writer(open("deplinks1240-1500.csv", 'a'))
        print('-----Scraping page: ' + row[0])
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
            base_url = "http://google.com/search?q="
            q = row[0] + " Departments"
            print(q)
            base_url += '+'.join(q.split())
            url = base_url + '&ie=utf-8&oe=utf-8'
            r = se.get(url, headers=headers_Get)
            print(url)
            print(r)
            soup = BeautifulSoup(r.text)
            new_emails = soup.find_all('a', href=True)
            for link in new_emails:
                if "http" in link['href'] and "maps" not in link['href']:
                    print(link['href'])
                    res = link['href']
                    res2 = res[res.find('http'):]
                    found = res2[:res2.find("&")]
                    print(found)
                    writer.writerow([found])
                    break

        except requests.RequestException:
            print('timeout')
