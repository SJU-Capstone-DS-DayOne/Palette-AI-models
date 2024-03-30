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

    time_button = driver.find_elements(By.CSS_SELECTOR, "._UCia")[1].click()        # 식당 시간 더보기 버튼 클릭
    time.sleep(2)
    rst_times =  driver.find_elements(By.CSS_SELECTOR, ".A_cdD")[1:]                # 요일별 영업시간들
    times = []
    for rst_time in rst_times:
        times.append(rst_time.text.replace("\n", " "))



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
region = '광진구'
word = ['음식점', '카페', '술집']
query = region + word[0]
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


infos, rst_lis, menu_lis, price_lis = [], [], [], []
columns = ['name', 'category', 'sub_category', 'address', 'opening_hours', 'contact', 'platform']
menu_columns = ['rst_name', 'menu_name', 'price']

result = 0 # 전체 식당 수
tag = 1

cnt=0 # test
while tag != -1:

    # 밑으로 최대한 내리기
    scroll_down()

    rsts = driver.find_elements(By.CSS_SELECTOR, ".UEzoS")
    for rst in rsts:
        if cnt == 3:
            break
        # test
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

        """
        정보 수집
        """
        info, rst_li, menu_li, price_li = crawl_rst_info(word[0])
        infos.append(info)
        rst_lis.extend(rst_li)
        menu_lis.extend(menu_li)
        price_lis.extend(price_li)


        # iframe 다시 레스토랑 전체 탭으로 복귀
        driver.switch_to.default_content()
        iframe = driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe")
        driver.switch_to.frame(iframe)
        time.sleep(2)
        print('----------------------------------------------------------------------------------------------------------------')
        print()
        # test
        cnt+=1

    if cnt == 3:
        break
        # test
    # result += len(rsts)
    # 다음 페이지
    tag = next_page()


# 리스트를 데이터프레임으로 변환
df_rst = pd.DataFrame(infos, columns=columns)
df_rst.to_csv("test.csv", encoding='cp949')

rst_menu = pd.DataFrame({menu_columns[0]:rst_lis,
                         menu_columns[1]:menu_lis,
                         menu_columns[2]:price_lis})
rst_menu.to_csv("restaurant_menu.csv", encoding='cp949')

# iframe에서 벗어나기
driver.switch_to.default_content()

print("Done-!!!")