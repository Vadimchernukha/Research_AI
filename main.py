# main.py
import asyncio
import aiohttp
import logging
import urllib3
import random
import csv
from datetime import datetime
import aiofiles
from tqdm import tqdm
import concurrent.futures
import time  # Для замера времени

from tasks.network import fetch_website_content
from tasks.parser import parse_html
from tasks.analysis import analyze_website_content
from tasks.csv_writer import format_csv_row
from tasks.fallback import fetch_headless  # fallback через Selenium
from prompts import PROMPT_SOFTWARE  # Ваш промпт
from config import API_KEY2  # Конфигурация

import openai

openai.api_key = API_KEY2
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настройка логирования: все логи записываются в processing.txt с кодировкой UTF-8
logging.basicConfig(
    filename="logs/processing.txt",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


async def append_row(row, file_handle, lock):
    """
    Асинхронная запись одной строки в CSV с немедленным сбросом буфера.
    """
    row_str = format_csv_row(row) + "\n"
    async with lock:
        await file_handle.write(row_str)
        await file_handle.flush()


async def process_website(session, url, prompt, include_comments, file_handle, write_lock, progress, pbar, metrics):
    """
    Обработка одного сайта: попытка получить HTML через обычный запрос,
    а если не удалось – fallback с использованием headless браузера.
    Если сайт признан релевантным, результат записывается в CSV.
    При этом замеряется время обработки, и обновляются метрики.
    """
    start_time = time.perf_counter()
    logging.info(f"Начало обработки сайта: {url}")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
    domain = url.replace("https://", "").replace("http://", "").split('/')[0]

    # Попытка получить HTML обычным запросом
    html = await fetch_website_content(session, url)

    # Если обычный запрос не сработал, пробуем fallback через headless браузер
    if not html:
        logging.info(f"Обычный запрос не сработал для {url}. Попытка fallback с headless браузером.")
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            html = await loop.run_in_executor(pool, fetch_headless, url)

    # Обработка полученного HTML
    if html:
        content = parse_html(html)
        if content:
            comment = analyze_website_content(content, prompt)
            if comment:
                row = [domain, comment] if include_comments else [domain]
                await append_row(row, file_handle, write_lock)
                logging.info(f"Сайт {url} обработан успешно (релевантен).")
                async with write_lock:
                    metrics["successful"] += 1
            else:
                logging.info(f"Сайт {url} не признан релевантным.")
                async with write_lock:
                    metrics["errors"] += 1
        else:
            logging.warning(f"Не удалось извлечь контент из {url}.")
            async with write_lock:
                metrics["errors"] += 1
    else:
        logging.error(f"Не удалось получить HTML для {url} даже через fallback.")
        async with write_lock:
            metrics["errors"] += 1

    processing_time = time.perf_counter() - start_time
    async with write_lock:
        metrics["total_time"] += processing_time
        progress["processed"] += 1
        percent = (progress["processed"] / progress["total"]) * 100
        logging.info(
            f"Обработано {progress['processed']}/{progress['total']} сайтов ({percent:.2f}%). Время обработки сайта: {processing_time:.2f} сек.")
        pbar.update(1)
        pbar.refresh()


async def process_websites(input_file, output_file, prompt, include_comments,
                           max_concurrent=50, batch_size=100):
    """
    Основной процесс: чтение URL из input_file, асинхронная обработка и параллельная запись результатов в output_file.
    Собираются и логируются метрики производительности.
    """
    write_lock = asyncio.Lock()
    # Инициализация метрик: общее время, количество успешных и неуспешных обработок
    metrics = {"total_time": 0.0, "successful": 0, "errors": 0}

    async with aiofiles.open(output_file, 'w', encoding='utf-8', newline='') as file_handle:
        # Записываем заголовок CSV
        header = format_csv_row(["Domain", "Comment"]) if include_comments else format_csv_row(["Domain"])
        await file_handle.write(header + "\n")

        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            urls = [row[0].strip() for row in reader if row]
        total_urls = len(urls)
        progress = {"processed": 0, "total": total_urls}
        connector = aiohttp.TCPConnector(limit=max_concurrent, ssl=False)

        # Используем tqdm для отображения прогресса в консоли
        pbar = tqdm(total=total_urls, desc="Обработка сайтов", dynamic_ncols=True)

        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(0, total_urls, batch_size):
                batch = urls[i:i + batch_size]
                await asyncio.sleep(random.uniform(2, 5))
                tasks = [
                    process_website(session, url, prompt, include_comments, file_handle, write_lock, progress, pbar,
                                    metrics)
                    for url in batch
                ]
                await asyncio.gather(*tasks)
                logging.info(f"✅ Завершён пакет сайтов с {i + 1} по {min(i + batch_size, total_urls)}")
        pbar.close()

    # Логируем сводные метрики
    average_time = metrics["total_time"] / progress["processed"] if progress["processed"] else 0
    logging.info(f"Обработка завершена: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(
        f"Общее время обработки: {metrics['total_time']:.2f} сек. Среднее время на сайт: {average_time:.2f} сек.")
    logging.info(f"Успешно обработано: {metrics['successful']} сайтов, ошибок: {metrics['errors']}.")
    logging.info("100% ✔️ Все сайты успешно обработаны!")


def main():
    input_file = "web.csv"
    output_file = "results.csv"
    user_choice = input("Включить комментарии в результаты? (y/n): ").strip().lower()
    include_comments = user_choice.startswith("y")
    prompt = PROMPT_SOFTWARE
    asyncio.run(process_websites(input_file, output_file, prompt, include_comments))
    print("Обработка завершена. Подробности см. в файле processing.txt.")


if __name__ == "__main__":
    main()
