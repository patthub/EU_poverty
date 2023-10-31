import requests
import os
from loguru import logger
import joblib
import urllib

proxies = {
  "http": "",
  "https": "",
}


def get_links_to_download(links_dir: str) -> list:
    links = []
    files = os.listdir(links_dir)
    for file in files:
        with open(os.path.join(links_dir, file), 'r') as f:
            links.extend(f.readlines())

    links = [link.strip() for link in links]
    logger.info(f'Found {len(links)} links to download')
    return links


def download_file(file_url: str, saving_dir: str) -> None:
    file_name_raw = file_url.split('/')[-1]
    # make hash to get file name
    file_name = str(abs(hash(file_name_raw)))
    logger.info(f'Downloading {file_name}')
    try:
        r = requests.get(file_url, allow_redirects=True, proxies=proxies, timeout=None)
        file_type =  urllib.request.urlopen(file_url).info()['content-type']
        if file_type == 'application/pdf':
            file_name += '.pdf'
        elif file_type == 'application/msword':
            file_name += '.doc'
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            file_name += '.docx'
        elif file_type == 'application/zip':
            file_name += '.zip'
        elif file_type == 'text/html':
            file_name += '.html'
        else: 
            print(file_type)
            with open('unknown_file_types.txt', 'a') as f:
                f.write(file_url + '\n')
                return None
        file_path = os.path.join(saving_dir, file_name)
        open(file_path, 'wb').write(r.content)
        logger.info(f'Downloaded {file_path}')
    except Exception as e:
        logger.error(f'Error downloading {file_url} with error {e}')
        with open('download_errors.txt', 'a') as f:
            f.write(file_url + '\n')


def main():
    links_dir = 'links'
    saving_dir = 'saved_files'
    links = get_links_to_download(links_dir)
    # download files in parallel
    joblib.Parallel(n_jobs=-1, verbose=100)(joblib.delayed(download_file)(link, saving_dir) for link in links)


if __name__ == '__main__':
    main()