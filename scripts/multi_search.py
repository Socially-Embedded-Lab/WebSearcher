import argparse
import time
import os
import sys
from pathlib import Path
import pandas as pd
from datetime import date

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import WebSearcher as ws

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, 
        help="A path for excel file with input queries, locations, and languages")
    parser.add_argument("-o", "--out_dir", type=str, help="A path for output")
    args = parser.parse_args()

    if not args.input:
        print('Must include -i arg for input xlsx.')
        return
    if not args.out_dir:
        print('Must include -o arg for output directory.')
        return

    # read input
    df = pd.read_excel(args.input)

    # create output directories
    today = str(date.today())
    html_dir = Path(args.out_dir) / 'html' / today
    screen_dir = Path(args.out_dir) / 'screenshot' / today
    html_dir.mkdir(parents=True, exist_ok=True)
    screen_dir.mkdir(parents=True, exist_ok=True)
    
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    for index, row in df.iterrows():
        loc = row['country']
        lang = row['langs']
        file_name = f"{row['term_id']}_{loc}_{lang}"
        html_path = str(html_dir / f'{file_name}.html')
        screen_path = str(screen_dir / f'{file_name}.png')

        # SEARCH
        se = ws.SearchEngine(accept_language=row['code_lang'])
        se.search(row['term'], location= loc)
        
        with open(html_path / f'{file_name}.html', 'wt') as f:
            f.write(se.html)

        se.screenshot('file://' + html_path, screenshot_path, driver)
        print(f'{file_name} done.\n')
        time.sleep(1)
