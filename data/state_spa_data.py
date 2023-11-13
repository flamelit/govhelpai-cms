import logging
import os
import re
import urllib.request
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
base_file_url = 'https://www.medicaid.gov/sites/default/files/'
base_index_url = 'https://www.medicaid.gov/medicaid/medicaid-state-plan-amendments/index.html?page={}'


def fetch_total_count(url):
    "Get total count"
    regex_str_first = 'Showing 1 to 10 of (\d+) results\n'
    return int(re.search(regex_str_first, requests.get(url).text).group(1))


def download_pdf(link, folder_path):
    response = requests.get(link)
    filename = link.split('/')[-1]

    with open(os.path.join(folder_path, filename), 'wb') as f:
        f.write(response.content)
    print(f"Downloaded {filename}")


def scrape_pdfs(url, folder_path=Path('./data/downloaded/')):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.pdf') and href.startswith('/sites/default/files'):
            logger.info(f'Fetching {href}')
            pdf_url = urllib.parse.urljoin(url, href)
            download_pdf(pdf_url, folder_path)
            logger.info(f'{href} fetched')

fullcount = fetch_total_count(base_index_url.format(0))

for i in list(range(1, fullcount%10 + 10))[:100]:
    logger.info(f'scraping page {i}')
    scrape_pdfs(base_index_url.format(i))
