# fallback.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def fetch_headless(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(5)  # Даем время на выполнение JavaScript и рендеринг страницы
        html = driver.page_source
    except Exception as e:
        html = None
    finally:
        driver.quit()
    return html
