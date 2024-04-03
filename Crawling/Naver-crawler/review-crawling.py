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
import random


# 네이버 플레이스 함수
def remove_emoji(text):
    # 이모지 패턴 정규 표현식
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # 스마일 이모티콘
                               u"\U0001F300-\U0001F5FF"  # 이모티콘 및 기호
                               u"\U0001F680-\U0001F6FF"  # 기호
                               u"\U0001F1E0-\U0001F1FF"  # 국기 표시 (1)
                               "]+", flags=re.UNICODE)
    # 이모지 제거
    return emoji_pattern.sub(r'', text)

def find_show_more():
    try:
        # '더보기' 버튼을 찾음
        b_tag = "#app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k1QQ5 > div.NSTUp > div > a > span"
        show_more_button = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, b_tag))
        )
        # 버튼 클릭
        show_more_button.click()
        time.sleep(2)

        return 1
    except:
        # 더 이상 '더보기' 버튼이 없으면 반복 종료
        return -1

def scroll_up():
    # 페이지 위로 스크롤
    driver.execute_script("arguments[0].scrollTop = 0;", driver.find_element(By.CSS_SELECTOR, ".place_section_header"))
    time.sleep(1)

def crawl_review(driver, rst_name):
    user = driver.find_element(By.CSS_SELECTOR, ".P9EZi").text                                  # 유저 이름

    time.sleep(0.05)

    # 리뷰 텍스트 전체보기 클릭
    try:
        more_button = driver.find_element(By.CSS_SELECTOR, ".WPk67")
        more_button.click()
        time.sleep(0.1)
    except:
        pass
    
    # 리뷰가 적혀있지 않은 경우, None으로 처리
    try:
        review_text = driver.find_element(By.CSS_SELECTOR, ".zPfVt").text.replace("\n", " ")    # 리뷰 텍스트
        review_text = remove_emoji(review_text)
    except:
        review_text = None
    
    u_rst_tag = []
    try:
        tags = driver.find_elements(By.CSS_SELECTOR, ".sIv5s")                                  # 유저가 리뷰에 남긴 태그
        for tag in tags:
            u_rst_tag.append(tag.text)
    except:
        tags = None
    
    try:
        date = driver.find_element(By.CSS_SELECTOR, ".CKUdu time").text                         # 리뷰 남긴 날짜
    except:
        date = None

    result = [rst_name, user, review_text, u_rst_tag, None, date, 0]                            # 리스트로 저장

    return result

def crawl_review_info(rst_name):
    try:
        tabs = driver.find_elements(By.CSS_SELECTOR, "._tab-menu")
        for tab in tabs:
            if tab.text == '리뷰':
                review_button = tab
                break                                                                           # 리뷰 버튼 클릭
        review_button.click()
        time.sleep(1)
    except:
        return []

    tag = 1
    # while tag != -1:
    for _ in range(150):
        tag = find_show_more()   
        if tag == -1:
            break                                                               
        # 끝까지 '더보기' 버튼 클릭
    
    print("\n리뷰 전체 로드 완료\n")
    print("---------------------------------------------------------------------------------------------------")
    time.sleep(0.05)

    results = []                                                                                # 레스토랑 하나 당 결과를 담을 리스트
    reviews = driver.find_elements(By.CSS_SELECTOR, ".owAeM")
    time.sleep(2)

    print("Review Info\n")
    print(f"해당 식당의 리뷰 개수는 {len(reviews)}입니다\n")
    for i, review in enumerate(reviews):
        result = crawl_review(review, rst_name)
        results.append(result)

        if i % 30 == 0:
            print(f"{i + 1}번째 리뷰")
            print(result)
            print()
            time.sleep(random.uniform(0, 0.2))

        time.sleep(0.1)
    print("리뷰 전체 수집 완료")
    
    return results

def switch_to_search_iframe(driver):
    # 지도가 아닌 검색 탭의 iframe으로 전환
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe")
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

def convert_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# Setting
# 크롬 드라이버 다운로드 및 자동 설정
chrome_driver_path = ChromeDriverManager().install()

# 브라우저 꺼짐 방지 옵션
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 불필요한 에러 메시지 삭제
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])


# 저장할 파일의 경로 설정
# E 드라이브의 MOON 폴더 경로. 데이터를 불러오고 저장해줄 경로
folder_path = "E:/MOON/capstone_data"
file_name = "자양동_음식점"
csv_path = os.path.join(folder_path, f"restaurant_{file_name}_naver.csv")

# Load data
data = pd.read_csv(csv_path)
urls = data['url']

# Open Chrome driver
print("Open Driver")
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
driver.maximize_window()
time.sleep(5)
print("Driver Opend\n\n")

# 크롤링 시작 시간 기록
start_time = time.time()

# 리뷰 정보 담을 리스트
results = []

print("Let's Start-!!\n")
# urls 리스트에서 첫 번째 요소는 이미 열렸으므로 두 번째 요소부터 처리
for url in urls[5:7]:
    driver.get(url)
    time.sleep(4)

    # 식당 정보 iframe 전환
    switch_to_info_iframe(driver)

    # 식당 이름 정보 수집
    name = driver.find_element(By.CSS_SELECTOR, ".Fc1rA").text
    print("===================================================================================================")
    print("Restaurant Name\n")
    print(name)
    print()

    # 리뷰 정보 수집
    result = crawl_review_info(name)
    results.extend(result)

print()
print("====================================================  Done  ============================================================")
print()
for _ in range(2):
    print("========================================================================================================================")
print()
print()

# 크롤링 종료 시간 기록
end_time = time.time()
# 크롤링 소요 시간 계산
elapsed_time = end_time - start_time
hours, minutes, seconds = convert_seconds(elapsed_time)
# 결과 출력
print("크롤링 소요 시간: {}시간 {}분 {}초\n".format(int(hours), int(minutes), int(seconds)))


# 마지막 탭 닫기
driver.close()

 # 리뷰 스키마
rev_cols = ['rst_name', 'user_name', 'review_text', 'u_rst_tag', 'ate_menus', 'date', 'platform']
df_review = pd.DataFrame(results, columns=rev_cols)

# 파일 경로와 파일명 설정
file_path = os.path.join(folder_path, f"review_{file_name}_naver.csv")

# info.csv 파일이 이미 존재하는지 확인하고 파일이 없으면 새로 생성하고 있으면 덮어쓰기
if not os.path.exists(file_path):
    df_review.to_csv(file_path, index=False, encoding='utf-8-sig')
    print("csv 파일을 생성하였습니다.")
else:
    df_review.to_csv(file_path, index=False, encoding='utf-8-sig', mode="a",header=False)
    print("csv 파일을 이어붙였습니다.")