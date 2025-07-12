import re
import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def word_tokenize(text):
    WORD = re.compile(r'\w+')
    words = list(set(word.lower() for word in WORD.findall(text)))

    return words


def extract_selected_info_from_url(url):
    """"""

    selected_info = {}

    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        try:
            driver.get(url)
            time.sleep(2)
            final_url = driver.current_url
            html = driver.page_source
        finally:
            driver.quit()
        soup = BeautifulSoup(html, 'html.parser')

        selected_info['title'] = soup.title.string

        meta_tags = []
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property") or tag.get("http-equiv")
            content = tag.get("content")
            if name and content:
                meta_tags.append((name, content))
        selected_info['meta'] = meta_tags

        base_url = final_url
        links = []
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True)
            text = " ".join(text.split())
            href = a['href'].strip()
            # Links without link text
            if not text:
                continue
            # Links without at least one letter or number are excluded.
            if not re.search(r'[a-zA-Z0-9äöüÄÖÜß]', text):
                continue
            # Remove links to foreign domains
            parsed_href = urlparse(href)
            parsed_base = urlparse(base_url)
            if parsed_href.netloc and parsed_href.netloc != parsed_base.netloc:
                continue
            # Convert relative links to absolute URLs
            abs_href = urljoin(base_url, href)

            links.append((text, abs_href))

        # Remove duplicates
        seen = set()
        unique_links = []
        for text, href in links:
            if (text, href) not in seen:
                seen.add((text, href))
                unique_links.append((text, href))

        # Sort by name in alphabetical order ascending
        links = sorted(unique_links, key=lambda x: x[0].lower())
        selected_info['links'] = links

        # Extract headings h1-h6 in order of appearance
        headings = []
        for tag in soup.find_all(re.compile(r'h[1-6]')):
            text = tag.find(text=True, recursive=False)
            if text:
                text = " ".join(text.strip().split())
                headings.append((text, tag.name.lower()))
        selected_info['headings'] = headings

    except Exception as e:
        print(e)
        print(e.__traceback__)

    return selected_info
