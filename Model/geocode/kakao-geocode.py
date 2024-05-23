import pandas as pd
import requests, json
from tqdm import tqdm
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

import config


# Data Load
path = "../data/"

restaurant = pd.read_csv(path + "restaurant_summary.csv", encoding='utf-8-sig')
review = pd.read_csv(path + "review.csv", encoding='utf-8-sig')

key = config.kakao_api_key
headers = {"Authorization": f"KakaoAK {key}"}

# Function
def get_location(address):
  url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + address
  
  api_json = json.loads(str(requests.get(url,headers=headers).text))
  
  address = api_json['documents'][0]['address']
  crd = {"lat": str(address['y']), "lng": str(address['x'])}

  return crd['lat'], crd['lng']

# main
for i in tqdm(range(len(restaurant))):
    restaurant_id = restaurant.loc[i, 'restaurant_id']
    restaurant_name = restaurant.loc[i, 'name']
    address = restaurant.loc[i, 'address']

    # 리뷰 카운트
    review_of_restaurant = review[review['restaurant_id'] == restaurant_id]
    review_count = len(review_of_restaurant)

    # 데이터 입력
    restaurant.loc[i, 'review_count'] = review_count

    try:
        # 위도, 경도 호출 및 입력
        lat, lng = get_location(address)
        restaurant.loc[i, 'lat'], restaurant.loc[i, 'lng'] = lat, lng
    except:
        print("\n"+restaurant_id, restaurant_name)
       
# Save
restaurant.to_csv(path + "restaurant_summary_geo_revcnt.csv", encoding='utf-8-sig', index=False)