import warnings
# 'UserWarning' 유형의 경고를 숨김
warnings.filterwarnings('ignore', category=UserWarning, message="Upper case characters found in vocabulary while 'lowercase' is True")
warnings.filterwarnings("ignore", message="torch.utils._pytree._register_pytree_node is deprecated. Please use torch.utils._pytree.register_pytree_node instead.")

from functions import *
import pandas as pd
import ast
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import CountVectorizer
# from transformers import BertModel
# from keybert import KeyBERT
from collections import defaultdict
import torch
import numpy as np
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

tqdm.pandas()

""" Data Load """

print("=" * 10, end="")
print(" Data Load ", end="")
print("=" * 10)

path = "./data/"
rst = pd.read_csv(path + "restaurant.csv", encoding='utf-8-sig')
menu = pd.read_csv(path + "menu_sample.csv", encoding='utf-8-sig')
rev = pd.read_csv(path + "review_sample.csv", encoding='utf-8-sig')

rev2input = review_table2input(rev)
menu2input = make_menu_list(menu)

""" Input Text Preprocessing """

print("=" * 10, end="")
print(" Input Text Preprocessing ", end="")
print("=" * 10)

# 가공된 리뷰, 메뉴 테이블을 조인하고 menu sentece 선별
# 'restaurant_id' 컬럼을 기준으로 조인
rev2input = rev2input[['restaurant_id', 'review_sentence_split']]

keybert_input = pd.merge(rev2input, menu2input, on='restaurant_id')
keybert_input = keybert_input[['restaurant_id', 'menu_id', 'review_sentence_split', 'menu_name_split', 'org_menu_dict']]

# 로드해서 string이 된 리스트를 다시 파이썬 리스트로 변환
try:
    keybert_input["review_sentence_split"] = keybert_input["review_sentence_split"].apply(ast.literal_eval)
except:
    pass
try:
    keybert_input["org_menu_dict"] = keybert_input["org_menu_dict"].apply(ast.literal_eval)
except:
    pass

try:
    keybert_input["menu_sentence"] = keybert_input["menu_sentence"].apply(ast.literal_eval)
except:
    pass

try:
    keybert_input["menu_name_split"] = keybert_input["menu_name_split"].apply(ast.literal_eval)
except:
    pass

try:
    keybert_input["review_sentence_split"] = keybert_input["review_sentence_split"].apply(ast.literal_eval)
except:
    pass

# 메뉴명:메뉴id 딕셔너리 생성성
keybert_input = map_menu_ids_to_dict(keybert_input)

# 데이터프레임 df에서 각 행에 대해 함수 적용
keybert_input['menu_sentence'] = keybert_input.apply(filter_menu_sentences, axis=1)
# input text 열 만들기
keybert_input['input_text'] = keybert_input['menu_sentence'].apply(doc_to_input_text)


""" KeyBERT로 대표메뉴 추출 """

print("=" * 10, end="")
print(" KeyBERT ", end="")
print("=" * 10)

# # KeyBERT 로드. (KoBERT 사용)
# model = BertModel.from_pretrained("skt/kobert-base-v1")
# # KeyBERT 모델 초기화 (skt의 Kobert 사용)
# kw_model = KeyBERT(model)

rst_name_list, menu_name_list, keybert_scores = [], [], []

output=[]
for i in tqdm(range(len(keybert_input)), desc="keybert", mininterval=0.1):
    # 식당의 문장 리스트 추출
    
    input_text = keybert_input.loc[i, 'input_text']
    menu_candidates=keybert_input.loc[i, 'menu_name_split']
    org_menu_dict=keybert_input.loc[i,'org_menu_dict']
    menu_name_id_dict = keybert_input.loc[i,'menu_name_id_dict']

    review = keybert_input.loc[i,'menu_sentence']
    rst_name = keybert_input.loc[i, 'restaurant_id']

    results = extract_keywords_with_candidate(input_text,menu_candidates)
    # print(results)

    # 메뉴 이름을 키로 하고 전처리된 메뉴명을 값으로 하는 새로운 딕셔너리 생성
    submenu_to_menu = {}
    for menu_dict in org_menu_dict:
        for key, values in menu_dict.items():
            for value in values:
                submenu_to_menu[value] = key

    menu_score = []
    if results:
        # 각 결과에 대해 df에 들어갈 각 행으로 변환
        for result in results:
            name, score = result[0], result[1]
            name = sub_to_org(name, submenu_to_menu)
            menu_score.append([name, score])
            
        # 같은 원본 메뉴 이름을 가진 것들의 중복 제거
        menu_score = duplicate_removed_list(menu_score)
        print(f"restaurant id = {rst_name}")
        for menu_name, score in menu_score:
            menu_id = menu_name_id_dict[menu_name]
            
            print((menu_id, menu_name, score), end=", ")
            rst_info = []

            rst_info.append(rst_name)
            rst_info.append(menu_id)
            rst_info.append(menu_name)
            rst_info.append(score)
            rst_info.append(review)
            rst_info.append(org_menu_dict)

            output.append(rst_info)

        del [[rst_info]]
        print()

print("=" * 10, end="")
print(" KeyBERT Done ", end="")
print("=" * 10)
print()


""" Sentiment Penalty """

print("=" * 10, end="")
print(" Sentiment Penalty ", end="")
print("=" * 10)

# 키버트 아웃풋 데이터프레임화
cols = ["restaurant_id", "menu_id", "main_menu", "keybert_score", "menu_reviews" ,"org_menu_dict"]
keybert_output=pd.DataFrame(output, columns=cols)

# filter_org_menu_dict 적용
keybert_output['filtered_org_menu_dict'] = keybert_output.apply(filter_org_menu_dict, axis=1)
# filter_reviews_by_menu 적용
keybert_output['filtered_reviews'] = keybert_output.apply(filter_reviews_by_menu, axis=1)


# load model
tokenizer = AutoTokenizer.from_pretrained("jaehyeong/koelectra-base-v3-generalized-sentiment-analysis")
model = AutoModelForSequenceClassification.from_pretrained("jaehyeong/koelectra-base-v3-generalized-sentiment-analysis")
sentiment_classifier = TextClassificationPipeline(tokenizer=tokenizer, model=model)

# 감성분석 함수 (0~1 사이 값으로 출력)
def get_sentiment_score(sentence):
    result = sentiment_classifier(sentence)[0]
    return result['score'] if result['label'] == '1' else 1-(result['score'])

def calculate_SP(sentences):
    positive_count = sum(1 for sentence in sentences if sentiment_classifier(sentence)[0]['label'] == '1')
    total_reviews = len(sentences)
    if total_reviews == 0:
        return 0  # 예외 처리: 리뷰가 없는 경우
    exponent_value = 1 - ((1 + total_reviews) / (1 + positive_count))
    # return (np.e + alpha) ** exponent_value
    return exponent_value

# 'reviews' 열의 문장 리스트를 사용하여 평균 감성 점수 계산
keybert_output['exponent_value'] = keybert_output['filtered_reviews'].progress_apply(calculate_SP)

# total_score 열 계산
alpha = 1

# alpha 반영하여 e^(alpha*exponent_value) 로 계산하는 식
keybert_output['Sentiment_Penalty'] = np.exp(keybert_output['exponent_value']*alpha)
keybert_output['total_score'] = keybert_output['keybert_score'] * keybert_output['Sentiment_Penalty']

# rst_name 열의 값이 같은 식당 별로 total_score가 높은 순으로 정렬
sorted_data = keybert_output.sort_values(by=['restaurant_id','total_score'], ascending=[True, False])

print("=" * 10, end="")
print(" Sentiment Penalty Done ", end="")
print("=" * 10)
print

""" Ranking """

print("=" * 10, end="")
print(" Ranking ", end="")
print("=" * 10)

# restaurant_id를 기준으로 두 데이터프레임 결합
# restaurant_id 컬럼을 문자열에서 정수형으로 변환
try:
    menu['restaurant_id'] = menu['restaurant_id'].astype(int)
except:
    pass
try:
    sorted_data['restaurant_id'] = sorted_data['restaurant_id'].astype(int)
except:
    pass
try:
    menu['menu_id'] = menu['menu_id'].astype(int)
except:
    pass
try:
    sorted_data['menu_id'] = sorted_data['menu_id'].astype(int)
except:
    pass

menu_sample_updated = assign_ranking(menu, sorted_data)


# combined_data = pd.merge(menu, sorted_data, on='restaurant_id')

# # 각 restaurant_id 그룹별로 처리
# menu['ranking'] = menu.apply(lambda row: update_ranking(row, combined_data[combined_data['restaurant_id'] == row['restaurant_id']]), axis=1)
# # total_score에 따라 순위 부여
# menu['ranking'] = menu.groupby('restaurant_id')['ranking'].rank(method='dense', ascending=False)


""" Save """
menu_sample_updated.to_csv(path + "ranked_menu.csv", encoding='utf-8-sig', index=False)


""" 개수 """
# ranking 열이 null이 아닌 행들만 필터링
filtered_menu_sample = menu_sample_updated[menu_sample_updated['ranking'].notna()]
nonfiltered_menu_sample = menu_sample_updated[~menu_sample_updated['ranking'].notna()]

print("대표메뉴가 존재하는   식당의  수:", filtered_menu_sample['restaurant_id'].nunique())
print("대표메뉴가 존재하지 않는 식당 수:", nonfiltered_menu_sample['restaurant_id'].nunique())