import yaml
import asyncio
import json
import pandas as pd
import logging
import coloredlogs
import coloredlogs
import logging
from concurrent.futures import ThreadPoolExecutor
import requests

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


async def load_data(
    file_path: str
):
    with open(file_path) as f:
        data = json.load(f)
    return data


async def check_data(
    index,
    data
):
    BIN = data['BIN']
    url = config['url']
    response = requests.post(url,
                    proxies={
                        'http': f'http://{config['proxy_user']}:{config['proxy_pass']}@{config['proxy']}',
                    } if config['proxy'] else None,
                    headers={
                        'Content-Type': 'application/json',
                        'Host': 'purchasealerts.visa.com',
                        'Origin': 'https://purchasealerts.visa.com',
                        'Referer': 'https://purchasealerts.visa.com/vca-web/check',
                        'Sec-CH-UA': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
                        'Sec-CH-UA-Mobile': '?0',
                        'Sec-CH-UA-Platform': '"Windows"',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
                    }, data=json.dumps({
                        'panPrefix': f'{BIN}000',
                        'countryCode': config['country_code'],
                    }))

    if response.status_code == 200:
        data = response.json()
        if data['eligibility'] == True:
            logger.info(f'[{index - config['offset']}/{config['limit']}]: BIN {BIN} hợp lệ')
        else:
            logger.warning(
                f'[{index - config['offset']}/{config['limit']}]: BIN {BIN} không hợp lệ, {data["errorCode"]}')
        return data['eligibility']
    elif response.status_code == 429:
        logger.error(
            f'Quá nhiều request, Thử lại sau {config["retry_after"]} phút')
        for i in range(int(config['retry_after']) * 60):
            logger.info(
                f'Đợi {int(config["retry_after"]) * 60 - i} giây...')
            await asyncio.sleep(1)
        return await check_data(index, data)
    elif response.status_code == 400:
        logger.warning(
            f'[{index - config['offset']}/{config['limit']}]: BIN {BIN} không hợp lệ, status code: {response.status_code}, {response.json().get("message")}')
        return False
    else:
        logger.critical(
            f'[{index - config['offset']}/{config['limit']}]: BIN {BIN} không hợp lệ, status code: {response.status_code}, {response.text}')
        return None


async def main():
    logger.critical(f'Starting the program with config:')
    logger.warning(f'File đọc dữ liệu: {config["file_path"]}')
    logger.warning(f'File lưu dữ liệu: {config["output_file_path"]}')
    logger.warning(f'Số luồng: {config["num_threads"]}')
    logger.warning(
        f'Proxy: {config["proxy"] if config["proxy"] else "Không có"}')
    logger.warning(
        f'Kiểm tra từ dòng {config["offset"]} đến dòng {config["offset"] + config["limit"]}')

    try:
        df = pd.read_csv(config['output_file_path'])

    except Exception as e:
        data = await load_data(config['file_path'])
        logger.info(f'Đọc dữ liệu xong, có {len(df)} dòng dữ liệu')
        df = pd.DataFrame(data)
        df = df[df['BIN'].notnull()]
        logger.warning(f'Sau khi lọc dữ liệu, còn lại {len(df)} dòng dữ liệu')
        df['is_valid'] = None
        df.to_csv(config['output_file_path'], index=False)
        logger.warning(f'Đã tạo file {config["output_file_path"]}')

    results = df['is_valid'].to_list()
    try:
        with ThreadPoolExecutor(max_workers=config['num_threads']) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    asyncio.run,
                    check_data(index, row)
                )
                for index, row in df[config['offset']:config['offset'] + config['limit']].iterrows()
            ]
            results[config['offset']:config['offset'] + config['limit']] = await asyncio.gather(*futures)
    finally:
        df['is_valid'] = results
        df.to_csv(config['output_file_path'], index=False)
        logger.critical(
            f'Kết quả đã được lưu vào file {config["output_file_path"]}')

if __name__ == '__main__':
    asyncio.run(main())
