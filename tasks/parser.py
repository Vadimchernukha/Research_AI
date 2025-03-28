# parser.py
from bs4 import BeautifulSoup
import re
import logging

MAX_CONTENT_LENGTH = 15000

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^A-Za-zА-Яа-я0-9 .,!?-]', '', text)
    return text.strip()

def parse_html(html, parser_type="lxml"):
    soup = BeautifulSoup(html, parser_type)
    key_sections = []
    if soup.title:
        key_sections.append(clean_text(soup.title.get_text(strip=True)))
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        key_sections.append(clean_text(meta_desc.get('content')))
    for tag in ["h1", "h2", "h3", "p", "ul", "ol"]:
        key_sections += [clean_text(el.get_text(strip=True)) for el in soup.find_all(tag)]
    nav = soup.find('nav')
    if nav:
        key_sections += [clean_text(link.get_text(strip=True)) for link in nav.find_all('a') if link.get_text(strip=True)]
    footer = soup.find('footer')
    if footer:
        key_sections.append(clean_text(footer.get_text(strip=True)))
    content = ' '.join(key_sections)
    if len(content) < 100:
        logging.info(f"Недостаточно контента на сайте, длина текста: {len(content)} символов")
        return None
    return content[:MAX_CONTENT_LENGTH]
