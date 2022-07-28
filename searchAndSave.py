import WebSearcher as ws
from datetime import date
import pandas as pd
import time
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import sys

def creat_dir(path):
    '''
    Args:
        path: to create haml and screenshot  folder, if doesnt exists.
    '''
    today = str(date.today())
    html_path = f'{path}/html/{today}'
    screen_path = f'{path}/screenshot/{today}'

    if not os.path.exists(html_path):
        os.makedirs(html_path)
    if not os.path.exists(screen_path):
        os.makedirs(screen_path)

path_folder = sys.argv[1]  #arg1
creat_dir(path_folder)
df = pd.read_excel("SciSearch_terms_with_code.xlsx")

today = str(date.today())

options = webdriver.ChromeOptions()
options.headless = True
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

for index, row in df.iterrows():
    loc = row['country']
    lang = row['langs']
    file_name = f"{row['term_id']}_{loc}_{lang}"
    se = ws.SearchEngine(accept_language=row['code_lang'])
    # SEARCH
    se.search(row['term'], location= loc)
    html_path = f'/{path_folder}/html/{today}/{file_name}.html'
    screenshot_path = f'/{path_folder}/screenshot/{today}/{file_name}.png'
    with open(html_path, 'wt') as f:
        f.write(se.html)

    se.screenshot('file://' + html_path, screenshot_path,driver)
    print(f'{file_name} done..\n')
    time.sleep(90)
