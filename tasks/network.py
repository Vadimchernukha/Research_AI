# network.py
import asyncio
import aiohttp
import random
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_RETRIES = 3
INITIAL_DELAY = 2

async def fetch_website_content(session, url, retries=MAX_RETRIES, delay=INITIAL_DELAY):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (X11; Linux x86_64) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) Mobile/15E148 Safari/537.36"
    ]
    for attempt in range(retries):
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com",
            "DNT": "1",
            "Connection": "keep-alive"
        }
        try:
            await asyncio.sleep(random.uniform(0.5, 2))
            async with session.get(url, headers=headers, timeout=10, ssl=False) as response:
                if response.status == 403:
                    logging.warning(f"403 Forbidden для {url}, пробуем другой User-Agent (попытка {attempt + 1})")
                    await asyncio.sleep(random.uniform(3, 7))
                    continue
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                html = await response.text()
                if not html.strip():
                    logging.warning(f"Пустая HTML-страница для {url}")
                    return None
                # Возвращаем сырой HTML
                return html
        except Exception as e:
            logging.error(f"Ошибка получения {url} (попытка {attempt + 1}): {e}")
            await asyncio.sleep(delay * (2 ** attempt))
    return None
