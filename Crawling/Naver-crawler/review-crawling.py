from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import os
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
        #app-root > div > div > div > div:nth-child(6) > div:nth-child(2) > div.place_section.k1QQ5 > div.NSTUp > div > a > span
        #app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k1QQ5 > div.NSTUp > div > a > span
        #app-root > div > div > div > div:nth-child(6) > div:nth-child(2) > div.place_section.k1QQ5 > div.NSTUp > div > a > span
        
        # b_tag = "#app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k1QQ5 > div.NSTUp > div > a > span"
        # b_tag = driver.find_elements(By.CSS_SELECTOR, ".owAeM")
        # show_more_button = WebDriverWait(driver, 20).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, b_tag))
        # )

        show_more_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".TeItc"))
        )
        # 버튼 클릭
        show_more_button.click()
        time.sleep(7)

        return 1
    except:
        # 더 이상 '더보기' 버튼이 없으면 반복 종료
        return -1

def scroll_up():
    # 페이지 위로 스크롤
    driver.execute_script("arguments[0].scrollTop = 0;", driver.find_element(By.CSS_SELECTOR, ".place_section_header"))
    time.sleep(1)

def crawl_review(driver, rst_name, url):
    user = driver.find_element(By.CSS_SELECTOR, ".P9EZi").text                                  # 유저 이름

    time.sleep(0.1)

    # 리뷰 텍스트 전체보기 클릭
    try:
        more_button = driver.find_element(By.CSS_SELECTOR, ".WPk67")
        more_button.click()
        time.sleep(0.5)
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

    result = [rst_name, user, review_text, u_rst_tag, None, date, 0, url]                            # 리스트로 저장

    return result

def crawl_review_info(rst_name, url):
    try:
        tabs = driver.find_elements(By.CSS_SELECTOR, "._tab-menu")
        for tab in tabs:
            if tab.text == '리뷰':
                review_button = tab
                break                                                                           # 리뷰 버튼 클릭
        review_button.click()
        time.sleep(5)
    except:
        return []

    time.sleep(1)
    tag = 1
    # while tag != -1:
    for _ in range(70):
        tag = find_show_more()
        time.sleep(2)   
        if tag == -1:
            break                                                               
        # 끝까지 '더보기' 버튼 클릭
    
    print("\n리뷰 전체 로드 완료\n")
    print("---------------------------------------------------------------------------------------------------")
    time.sleep(0.05)

    results = []                                                                                # 레스토랑 하나 당 결과를 담을 리스트
    reviews = driver.find_elements(By.CSS_SELECTOR, ".owAeM")
    time.sleep(1)

    print("Review Info\n")
    print(f"해당 식당의 리뷰 개수는 {len(reviews)}입니다\n")
    for i, review in enumerate(reviews):
        result = crawl_review(review, rst_name, url)
        results.append(result)

        if i % 30 == 0:
            print(f"{i + 1}번째 리뷰")
            print(result)
            print()
            time.sleep(random.uniform(0, 0.2))

        time.sleep(0.05)
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
    time.sleep(1)

    # 새로 생긴 식당 탭 iframe으로 전환
    iframe = driver.find_element(By.CSS_SELECTOR, "#entryIframe")
    driver.switch_to.frame(iframe)
    time.sleep(1)

def convert_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds

def save(file_path):
    global results

    print(f"\n현재까지 수집한 리뷰 개수 = {len(results)}\n")
    # 리뷰 스키마
    rev_cols = ['rst_name', 'user_name', 'review_text', 'u_rst_tag', 'ate_menus', 'date', 'platform', 'url']
    df_review = pd.DataFrame(results, columns=rev_cols)

    # 파일 경로와 파일명 받아 저장

    # info.csv 파일이 이미 존재하는지 확인하고 파일이 없으면 새로 생성하고 있으면 덮어쓰기
    if not os.path.exists(file_path):
        df_review.to_csv(file_path, index=False, encoding='utf-8-sig')
        print("csv 파일을 생성하였습니다.")
    else:
        df_review.to_csv(file_path, index=False, encoding='utf-8-sig', mode="a",header=False)
        print("csv 파일을 이어붙였습니다.")
    
    # 중복된 리뷰 저장 방지 위해 리스트 비워주기
    del results
    results = []

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
# folder_path = "C:/Users/Administrator/capstone-ds/data"

# git에 데이터 올려놓고 실습실에서 불러올 때 쓰려함
folder_path = "../data"

file_names = ['홍대_음식점', '홍대_카페', '홍대_술집', '잠실_음식점', '잠실_카페', '잠실_술집']
file_name = file_names[0]
# csv_path = os.path.join(folder_path, f"df_{file_name}_cleaned.csv")

# Load data
data = pd.read_csv(folder_path + f"/restaurant_{file_name}.csv", encoding='utf-8-sig')
urls = data['url']


# Open Chrome driver
print("Open Driver")
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
driver.maximize_window()
time.sleep(3)
print("Driver Opened\n\n")

# 크롤링 시작 시간 기록
start_time = time.time()

# 리뷰 정보 담을 리스트
results = []

print("Let's Start-!!\n")

# 시작과 끝 번호를 지정해주세요. 이는 파일 저장할 때에도 적용됩니다
# 홍대
# 음식점 190, 카페 162, 술집 208
# 잠실
# 음식점 212, 카페 159, 술집 177
# start = 0
# end = 2

# 저장할 파일의 이름
file_path = folder_path + f"/review_{file_name}.csv"

for i, url in enumerate(urls):
    driver.get(url)
    time.sleep(5)

    # 식당 정보 iframe 전환
    switch_to_info_iframe(driver)

    # 식당 이름 정보 수집
    try:
        name = driver.find_element(By.CSS_SELECTOR, ".GHAhO").text
    except:
        # 진행중 식당 정보가 사라진 url 발견됨. 넘겨서 해결
        continue
    print("===================================================================================================")
    print(f"Restaurant Name_{i}\n")
    print(name)
    print()

    # 리뷰 정보 수집
    try:
        result = crawl_review_info(name, url)
        results.extend(result)

        del result
    except:
        # 중간에 튕긴 경우 지금까지 수집한 것들만 저장
        save(file_path)

    # 다섯번째마다 저장하여 메모리 저장량도 아끼고 혹시 모를 에러에 대응
    if i % 5 == 0:
        save(file_path)
    

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

if len(results) > 0:
    save(file_path)