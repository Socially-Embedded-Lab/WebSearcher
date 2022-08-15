import argparse
import time
import os
import sys
from pathlib import Path
import pandas as pd
from datetime import date

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

import WebSearcher as ws

def screenshot(url, save_path, driver, implicit_wait=10, render_wait=8):
    driver.implicitly_wait(implicit_wait)
    driver.get(url)
    time.sleep(render_wait)

    S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    driver.set_window_size(S('Width'), S('Height'))
    driver.find_element('tag name', 'body').screenshot(save_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, 
        help="A path for excel file with input queries, locations, and languages")
    parser.add_argument("-o", "--out_dir", type=str, help="A path for output")
    args = parser.parse_args()

    if not args.input:
        print('Must include -i arg for input xlsx.')
        sys.exit(1)
    if not args.out_dir:
        print('Must include -o arg for output directory.')
        sys.exit(1)

    # read input
    df = pd.read_csv(args.input)

    # create output directories
    # today = str(date.today())
    html_dir = Path(args.out_dir) / 'html'
    screen_dir = Path(args.out_dir) / 'screenshot'
    html_dir.mkdir(parents=True, exist_ok=True)
    screen_dir.mkdir(parents=True, exist_ok=True)
    
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-dev-shm-usage");
    options.add_argument('--disable-crash-reporter')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-extensions")
    options.add_argument("start-maximized");
    options.add_argument("disable-infobars");
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options)


    screenshot_list = []
    for index, row in df.iterrows():
        loc = row['country']
        lang = row['langs']
        file_name = f"{row['term_id']}_{loc}_{lang}"
        html_path = str(html_dir / f'{file_name}.html')
        screen_path = str(screen_dir / f'{file_name}.png')

        # SEARCH
        se = ws.SearchEngine(accept_language=row['code_lang'])
        se.search(row['term'], location= loc)
        
        with open(html_path, 'wt') as f:
            f.write(se.html)
        print(f'HTML for {file_name} saved.\n')
        screenshot_list.append((html_path, screen_path))

        time.sleep(1)

    for html_path, screen_path in screenshot_list:
        screenshot('file://' + html_path, screen_path, driver)
        print(f'Screenshot saved to {screen_path}.\n')
        