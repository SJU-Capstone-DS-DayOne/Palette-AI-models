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
        # print("click")

    time.sleep(3)

# 식당정보 수집
def crawl_rst_info(word):
    try:
        rst_name = driver.find_element(By.CSS_SELECTOR, ".Fc1rA").text              # 식당이름
    except:
        rst_name = None
    try:
        rst_category =  driver.find_element(By.CSS_SELECTOR, ".DJJvD").text         # 식당 카테고리
    except:
        rst_category = None
    try:
        rst_address =  driver.find_element(By.CSS_SELECTOR, ".LDgIH").text          # 식당 주소
    except:
        rst_address = None
    try:
        rst_number = driver.find_element(By.CSS_SELECTOR, ".xlx7Q").text            # 식당 전화번호
    except:
        rst_number = None

    try:
        time_button = driver.find_elements(By.CSS_SELECTOR, "._UCia")[1].click()        # 식당 시간 더보기 버튼 클릭
        time.sleep(3)
        rst_times =  driver.find_elements(By.CSS_SELECTOR, ".A_cdD")[1:]                # 요일별 영업시간들
        times = []
        for rst_time in rst_times:
            times.append(rst_time.text.replace("\n", " "))
    except:
        times = None



    tabs = driver.find_elements(By.CSS_SELECTOR, "._tab-menu")
    for tab in tabs:
        if tab.text == '메뉴':
            menu_button = tab                                                       # 메뉴 정보 수집

    menu_button.click()
    time.sleep(1)
    menus_tab = driver.find_elements(By.CSS_SELECTOR, ".E2jtL")
    
    menu_li = []
    price_li = []
    rst_li = []
    for menu in menus_tab:
        try:
            title = menu.find_element(By.CSS_SELECTOR, ".lPzHi").text
        except:
            title = None
        try:
            price = menu.find_element(By.CSS_SELECTOR, ".GXS1X")
            price = price.find_element(By.TAG_NAME, "em").text                      # 가격 정보 함께 수집
        except:
            price = None

        rst_li.append(rst_name)
        menu_li.append(title)
        price_li.append(price)
        

    print(rst_name)       # clear
    print(rst_category)   # clear
    print(rst_address)    # clear
    print(rst_number)     # clear
    print(times)          # clear
    print(menu_li)        # clear
    print(price_li)       # clear

    rst_info = [rst_name, word, rst_category, rst_address, times, rst_number, 0]

    return rst_info, rst_li, menu_li, price_li

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
        show_more_button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.TeItc'))
        )
        # 버튼 클릭
        show_more_button.click()
        time.sleep(2)

        return 1
    except:
        # 더 이상 '더보기' 버튼이 없으면 반복 종료
        return -1

def crawl_review(driver, rst_name):
    user = driver.find_element(By.CSS_SELECTOR, ".P9EZi").text                                  # 유저 이름

    time.sleep(1)

    # 리뷰 전체보기 클릭
    try:
        more_button = driver.find_element(By.CSS_SELECTOR, ".WPk67")
        more_button.click()
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
        pass
    
    try:
        date = driver.find_element(By.CSS_SELECTOR, ".CKUdu time").text                         # 리뷰 남긴 날짜
    except:
        date = None

    result = [rst_name, user, review_text, u_rst_tag, None, date, 0]                            # 리스트로 저장

    return result

def crawl_review_info(rst_name):
    tabs = driver.find_elements(By.CSS_SELECTOR, "._tab-menu")
    for tab in tabs:
        if tab.text == '리뷰':
            review_button = tab
            break                                                                                   # 리뷰 정보 수집
    review_button.click()
    time.sleep(3)
    
    # for i in range(1):
    #     find_show_more()  # test
    tag = 1
    while tag != -1:
        tag = find_show_more()                                                          # 끝까지 '더보기' 버튼 클릭
        
    
    print("\n리뷰 전체 로드 완료")
    print()
    results = []                                                                                    # 레스토랑 하나 당 결과를 담을 리스트
    reviews = driver.find_elements(By.CSS_SELECTOR, ".owAeM")

    print("Review Info")
    print()
    print(f"해당 식당의 리뷰 개수는 {len(reviews)}입니다")
    print()
    for i, review in enumerate(reviews):
        result = crawl_review(review, rst_name)
        results.append(result)

        if i % 30 == 0:
            print(f"{i}번째 리뷰 수집 완료입니다")
            print(result)
            print()

        time.sleep(1)
    print("리뷰 전체 수집 완료")
    
    return results  

def crawling_and_save(driver, q_, path):
    infos, rst_lis, menu_lis, price_lis = [], [], [], []    # 식당에 정보 저장하는 리스트
    results = []   

    tag = 1
    # query에 대해 크롤링 수행
    while tag != -1:
        # 밑으로 최대한 내리기
        scroll_down()

        # 레스토랑 및 리뷰 정보 수집
        rsts = driver.find_elements(By.CSS_SELECTOR, ".UEzoS")
        for rst in rsts:
            rst = rst.find_element(By.CSS_SELECTOR, ".tzwk0")

            # 레스토랑 방문
            rst.click()
            time.sleep(2)

            # 전체 페이지로 복귀하도록 iframe에서 벗어나기 -> 그래야만 새로 생긴 iframe 탭에 접근할 수 있음
            driver.switch_to.default_content()

            # 새로 생긴 식당 탭 iframe으로 전환
            iframe = driver.find_element(By.CSS_SELECTOR, "#entryIframe")
            driver.switch_to.frame(iframe)
            time.sleep(2)
            print("식당 탭 iframe 전환")
            print('----------------------------------------------------------------------------------------------------------------')
            print("Restaurant Info")
            print()
            """
            정보 수집
            """
            # 크롤링 시작 시간 기록
            start_time = time.time()

            # 식당 정보 수집
            info, rst_li, menu_li, price_li = crawl_rst_info(word[0])
            infos.append(info)              # 식당 정보
            rst_lis.extend(rst_li)          # 식당 이름 리스트 (식당/메뉴/가격 테이블용)
            menu_lis.extend(menu_li)
            price_lis.extend(price_li)

            # 식당에 대한 리뷰 수집
            time.sleep(3)
            result = crawl_review_info(info[0])
            results.extend(result[1:])             # 이유는 모르겠지만 리뷰 중 첫번째가 전체 로드되지 않는 이슈 발생해 첫 번째 제외

            # 크롤링 종료 시간 기록
            end_time = time.time()
            # 크롤링 소요 시간 계산
            elapsed_time = end_time - start_time
            print("크롤링 소요 시간:", elapsed_time, "초")

            """
            정보 수집 완료
            """
            # iframe 다시 레스토랑 전체 탭으로 복귀
            driver.switch_to.default_content()
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe")
            driver.switch_to.frame(iframe)
            time.sleep(random.uniform(1, 3))
            print('----------------------------------------------------------------------------------------------------------------')
            print()

        # 다음 페이지
        tag = next_page()

    # 쿼리에 대한 크롤링 정보 저장
    # 리스트를 데이터프레임으로 변환

    # 식당 스키마
    rst_cols = ['name', 'category', 'sub_category', 'address', 'opening_hours', 'contact', 'platform']
    df_rst = pd.DataFrame(infos, columns=rst_cols)
    df_rst.to_csv(path + f"/restaurant_{q_}.csv", encoding='cp949')

    # 메뉴 스키마
    menu_cols = ['rst_name', 'menu_name', 'price']
    rst_menu = pd.DataFrame({menu_cols[0]:rst_lis,
                            menu_cols[1]:menu_lis,
                            menu_cols[2]:price_lis})
    rst_menu.to_csv(path + f"/restaurant_menu_{q_}.csv", encoding='cp949')

    # 리뷰 스키마
    rev_cols = ['rst_name', 'user_name', 'review_text', 'u_rst_tag', 'ate_menus', 'date', 'platform']
    df_review = pd.DataFrame(results, columns=rev_cols)
    df_review.to_csv(path + f"/review.csv_{q_}", encoding='utf-8-sig')

    # iframe에서 벗어나 전체 페이지로 복귀
    driver.switch_to.default_content()

    print(f"{q_} Done-!!!")
    print("=========================================================================================================================")
    print("=========================================================================================================================")
    print("=========================================================================================================================")
    print()
    print()
    time.sleep(30)

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

# 크롬 브라우저를 열고 네이버 맵 keyword로 이동
print("Let's Start-!!")
region = ['중곡동', '군자동', '능동', '화양동', '자양동', '구의동', '광장동']
words = ['음식점', '카페', '술집']
query = region[0] + " " + words[0]

# 저장할 파일의 경로 설정
path = "E:/MOON/capstone_data"  # E 드라이브의 MOON 폴더 경로. 데이터를 저장해줄 경로

for word in words:
    query = region[0] + " " + word
    q_ = region[0] + "_" + word

    url = f"https://map.naver.com/p/search/{query}"
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    driver.get(url)
    driver.maximize_window()
    time.sleep(5)

    # 지도가 아닌 검색 탭의 iframe으로 전환
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe")
    driver.switch_to.frame(iframe)
    time.sleep(3)
    print("iframe 전환")

    # query에 대한 정보 수집과 csv파일 저장까지 완료
    crawling_and_save(driver, q_, path)
