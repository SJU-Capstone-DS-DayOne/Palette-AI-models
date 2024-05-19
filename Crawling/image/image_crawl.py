import selenium
from selenium.webdriver.common.by import By
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from openpyxl import Workbook
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
import mouseinfo
import time
import datetime
import requests
import random
import os
import pandas as pd
from tqdm import tqdm
import urllib.request

"""-----------------------------------------------------Functions-----------------------------------------------------"""
def create_folder(dir):
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except OSError:
        print("Create Folder Error !!!")


def switch_to_entry_iframe(driver):
    # 식당 탭으로 이동
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe#entryIframe")
    driver.switch_to.frame(iframe)
    time.sleep(3)
    print("iframe 전환")


def switch_to_info_iframe(driver):
    # 전체 페이지로 복귀하도록 iframe에서 벗어나기 -> 그래야만 새로 생긴 iframe 탭에 접근할 수 있음
    driver.switch_to.default_content()
    time.sleep(0.5)

    # 새로 생긴 식당 탭 iframe으로 전환
    iframe = driver.find_element(By.CSS_SELECTOR, "#entryIframe")
    driver.switch_to.frame(iframe)
    time.sleep(1)


"""-----------------------------------------------------Data Load-----------------------------------------------------"""
rst_info = pd.read_csv("../data/df_광진구음식점_cleaned.csv", encoding="utf-8-sig")
menu_info = pd.read_csv("../data/restaurant_menu_광진구음식점.csv",encoding='utf-8-sig')
# 나중에 다른 데이터프레임 불러와서 동시에 보면서해야됨
"""-----------------------------------------------------Chrome Driver Setting-----------------------------------------"""
options = Options()

# Chrome의 binary path 지정
options.binary_location = (
    "/Users/powerjsv/Desktop/Google Chrome.app/Contents/MacOS/Google Chrome"
)

# 불필요한 에러 메시지 삭제
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# 최대화
options.add_argument("--start-maximized")
# 크롬 드라이버 경로 알아서 맞출 것
chrome_driver_path = (
    "/Users/powerjsv/Desktop/project/capstone/chromedriver-mac-arm64/chromedriver"
)

driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
driver.implicitly_wait(2)

"""-----------------------------------------------------Crawling-----------------------------------------""" 
