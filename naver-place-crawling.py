from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import requests
import re
from time import sleep


# 네이버 플레이스 함수
def scroll_down():
    # 한 번에 10개의 식당이 나오고, 스크롤 시 동적으로 추가되어 총 50개까지 한 페이지 안에 나온다
    for i in range(4):
        # 페이지 아래로 스크롤
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", driver.find_element(By.CSS_SELECTOR, "#_pcmap_list_scroll_container"))
        time.sleep(3)

def next_page():

    # '>' 버튼 찾기
    next_button = driver.find_elements(By.CSS_SELECTOR, ".eUTV2")[-1]
    if next_button.get_attribute("aria-disabled") == 'true':
        print("Last Page")
        return -1

    else:
        next_button.click()
        print("click")

    time.sleep(3)

# Setting
# 크롬 드라이버 다운로드 및 자동 설정
chrome_driver_path = ChromeDriverManager().install()

# 브라우저 꺼짐 방지 옵션
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 불필요한 에러 메시지 삭제
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# 크롬 브라우저를 열고 cbs news 웹페이지로 이동
keyword = '광진구음식점'
url = f"https://map.naver.com/p/search/{keyword}"
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
driver.get(url)
driver.maximize_window()
time.sleep(5)


# iframe으로 전환
iframe = driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe")
driver.switch_to.frame(iframe)
time.sleep(3)
print("iframe 전환")

result = 0 # 전체 식당 수
tag = 1
while tag != -1:
    # 밑으로 최대한 내리기
    scroll_down()

    """
    정보 수집
    """
    rsts = driver.find_elements(By.CSS_SELECTOR, ".UEzoS")
    result += len(rsts)
    # 다음 페이지
    tag = next_page()

# iframe에서 벗어나기
driver.switch_to.default_content()

print("광진구 음식점 수 =", result)