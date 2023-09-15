import aiofiles
import aiohttp
import argparse
import asyncio
from multiprocessing import Process
from threading import Thread
import time
import requests


def default(url_list):
    for url in url_list:
        download(url)


def use_threads(url_list):
    threads = list()
    for url in url_list:
        thread = Thread(target=download, args=[url])
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def use_multiprocessing(url_list):
    processes = list()
    for url in url_list:
        process = Process(target=download, args=(url,))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()


def use_async(url_list):
    asyncio.run(async_task(url_list))


async def async_task(url_list):
    tasks = []
    for url in url_list:
        filename = get_filename(url)
        if filename.endswith(".jpg"):
            task = asyncio.ensure_future(async_download(url, filename))
            tasks.append(task)
    await asyncio.gather(*tasks)


async def async_download(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                start_time = time.time()
                img = await aiofiles.open(".\\download\\" + filename, mode='wb')
                await img.write(await response.read())
                await img.close()
                print(f"Download success {filename}. Loading time: {time.time() - start_time:.4f} sec.")


def download(url):
    filename = get_filename(url)
    if filename.endswith(".jpg"):
        response = requests.get(url)
        with open(".\\download\\" + filename, "wb") as f:
            start_time = time.time()
            f.write(response.content)
        print(f"Download success {filename}. Loading time: {time.time() - start_time:.4f} sec.")


def get_filename(url):
    return url.split("/")[-1].lower()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Загрузка изображений")
    parser.add_argument("-u", "--urls", nargs='+', type=str, help="Список URL‑адресов разделенных пробелом")
    parser.add_argument("-f", "--file", type=argparse.FileType('r'), help="Файл с URL-адресами")
    parser.add_argument('-th', '--threads', dest='mode', action='store_const', const=use_threads, default=default,
                        help='Загрузка в многопоточном режиме (по умолчанию: пошаговое выполнение программы)')
    parser.add_argument('-mp', '--multiprocessing', dest='mode', action='store_const', const=use_multiprocessing,
                        default=default,
                        help='Загрузка в мультипроцессорном режиме (по умолчанию: пошаговое выполнение программы)')
    parser.add_argument('-as', '--async', dest='mode', action='store_const', const=use_async, default=default,
                        help='Загрузка в асинхронном режиме (по умолчанию: пошаговое выполнение программы)')
    args = parser.parse_args()
    prog_time = time.time()

    if args.file:
        with args.file as file:
            url_list = file.read().split("\n")
            args.mode(url_list)

    if args.urls:
        url_list = args.urls
        args.mode(url_list)

    end_time = time.time() - prog_time
    print(f"Execute time:  {end_time:.2f} sec.")
