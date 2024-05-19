import pandas as pd
import re
from kiwipiepy import Kiwi
from collections import defaultdict
import ast
from transformers import BertModel
from keybert import KeyBERT

""" 인풋 텍스트 전처리 """
def drop_short_words(df, threshold):
    # 텍스트가 없는 널값 제거
    df = df.dropna(subset=['content'])

    # 한 단어 이상인 것들만 남기기
    df['word_counts'] = df['content'].apply(lambda x: len(x.split()))

    # 한 단어(threshold) 이상인 것들만 필터링하여 새로운 데이터프레임 반환. 필요없는 word_counts는 삭제
    return df[df['word_counts'] > threshold].drop(columns=['word_counts'])

def preprocess_emoji(content):
    filtered_content = re.sub(r'[^\s\wㄱ-힣\d]', '', content)
    
    return filtered_content

kiwi = Kiwi()
def kiwi_to_sentences(combined_review):

    sentences = kiwi.split_into_sents(combined_review)

    # 출력 형식 중 텍스트만 리스트에 저장
    text_list = [sentence.text for sentence in sentences]
    
    return text_list

def review_table2input(review_table):
    # 필요 컬럼만 선별
    review_table = review_table[['restaurant_id', 'content']]

    # 2단어 이상인 리뷰만 선별 (2단어인 이유는 중간발표 appendix. word count 히스토그램 참고)
    dropped_review_table = drop_short_words(review_table, 1)

    # 'review_text' 열에 정규 표현식 함수 적용
    dropped_review_table['content'] = dropped_review_table['content'].apply(preprocess_emoji)

    # restaurant_id로 그룹화하여 content(review_text)들을 온점 단위로 합치기
    grouped_reviews = dropped_review_table.groupby('restaurant_id')['content'].apply(lambda x: ' . '.join(x)).reset_index()

    # 새로운 데이터프레임 생성 및 문장 단위 분리해 리스트 저장
    new_df = pd.DataFrame(grouped_reviews)
    new_df['review_sentence_split'] = new_df['content'].apply(kiwi_to_sentences)

    return new_df

def map_menu_ids_to_dict(input_df):
    # 메뉴명과 아이디를 매핑하여 컬럼으로 저장하는 함수

    # 결과 딕셔너리 초기화
    menu_id_dicts = []
    
    # 각 행에 대해 처리
    for index, row in input_df.iterrows():
        # 데이터프레임의 각 행에 대해
        menu_ids = row['menu_id']
        menu_names = row['menu_name_split']
        org_dict = row['org_menu_dict']
        
        # 메뉴 ID와 카테고리를 매핑할 딕셔너리
        mapping = {}
        for menu_id, menu_dict in zip(menu_ids, org_dict):
            menu_name = next(iter(menu_dict.keys()))
            mapping[menu_name] = menu_id
        
        # 이 행의 결과를 추가
        menu_id_dicts.append(mapping)
    
    # 새로운 컬럼으로 결과 저장
    input_df['menu_name_id_dict'] = menu_id_dicts
    
    return input_df

""" 메뉴 문장 추출 """

# 메뉴 문장 추출

# 메뉴 데이터에서 메뉴 리스트를 먼저 만들어줍니다
# 추후 이 데이터를 활용해 리뷰에서 메뉴 문장만을 추출합니다

def remove_bracket_contents(menu_names):
    cleaned_list = []

    # 괄호 안의 내용을 모두 지우는 정규 표현식 패턴
    pattern = r'[\[\(].*?[\]\)]'

    for menu_name in menu_names:

        # 패턴을 사용하여 텍스트에서 괄호 안의 내용을 모두 지움
        cleaned_text = re.sub(pattern, '', menu_name)

        if cleaned_text is not None:
            cleaned_list.append(cleaned_text)

    return cleaned_list

def split_menu(menu_names):
    menu_sample_list = []
    menu_dict = []

    for menu_name in menu_names:
        org_menu_dict = {}
        split_result = re.split(r'[+\-\s]+', menu_name)

        # 원본 메뉴명에 대해 딕셔너리 키 생성
        if menu_name not in org_menu_dict:
            org_menu_dict[menu_name] = []  # 초기 리스트 생성


        # 띄어쓰기 단위로 잘라진 메뉴 이름 저장시키기
        menu_name_list = []

        tokened_blank_menu_list = []
        for result in split_result:
            if any(char.isdigit() for char in result):
                # 숫자일 경우 무시
                continue
            else:
                # " ", ""으로 조인시킬 메뉴 네임 리스트(임시적인 리스트)
                menu_name_list.append(result)

                # 얻어진 메뉴명을 토크나이즈 해주고 그것도 메뉴 리스트에 포함
                kiwi_tokens = kiwi.tokenize(result)
                tokened_blank_menu = " ".join([token.form for token in kiwi_tokens])
                tokened_blank_menu_list.append(tokened_blank_menu)

            tokened_blank_menu_join = " ".join(tokened_blank_menu_list)
            # 딕셔너리에 원본 메뉴명의 변형본 추가와 메뉴 샘플리스트에 넣기
            org_menu_dict[menu_name].append(tokened_blank_menu_join)
            menu_sample_list.append(tokened_blank_menu_join)

        menu_dict.append(org_menu_dict)

        
        blank_menu = " ".join(menu_name_list)
        contiuous_menu = "".join(menu_name_list)

        menu_sample_list.append(blank_menu)
        menu_sample_list.append(contiuous_menu)

        # 원본 메뉴 명의 변형을 딕셔너리에 저장
        org_menu_dict[menu_name].append(blank_menu)
        org_menu_dict[menu_name].append(contiuous_menu)
        org_menu_dict[menu_name] = list(set(org_menu_dict[menu_name]))

        # +, -, 공백 단위로 띄워준 메뉴 이름을 리스트에 넣어줌
        # split_result = re.split(r'[+\-\s]+', menu_name)
        # menu_sample_list.extend(split_result)

        # for result in split_result:
        #     # 얻어진 메뉴명을 토크나이즈 해주고 그것도 메뉴 리스트에 포함
        #     kiwi_tokens = kiwi.tokenize(result)
        #     menu_sample_list.extend([token.form for token in kiwi_tokens])

    # 리스트를 set으로 변환하여 중복 제거
    menu_sample_list = set(menu_sample_list)
    # set을 다시 리스트로 변환
    menu_sample_list = list(menu_sample_list)
    
    return menu_sample_list, menu_dict

def make_menu_list(df_menu):
    # 'rst_name'을 기준으로 그룹지어서 'menu_name' 열의 모든 값을 리스트로 모으기
    grouped = df_menu.groupby('restaurant_id').agg({
        'name': lambda x: list(x),
        'menu_id': lambda x: list(x)
    })
    
    grouped['preprocessed_menu_name'] = grouped['name'].apply(remove_bracket_contents)

    # 'menu_name' 열의 각 값들을 띄어쓰기 단위로 분할하여 리스트로 만들기
    grouped[['menu_name_split', 'org_menu_dict']] = grouped['preprocessed_menu_name'].apply(split_menu).apply(pd.Series)

    return grouped

def filter_menu_sentences(row):
    # review_sentence_split의 각 문장에 대해
    filtered_sentences = []
    
    sentences = row['review_sentence_split']
    for sentence in sentences:
        # sentence가 menu_name_split의 단어들을 포함하는지 확인
        if any(menu_word in sentence for menu_word in row['menu_name_split']):
            filtered_sentences.append(sentence)
    return filtered_sentences


def filter_non_menu_sentences(row):
    # review_sentence_split의 각 문장에 대해
    filtered_sentences = []
    
    sentences = row['review_sentence_split']
    for sentence in sentences:
        # sentence가 menu_name_split의 단어들을 포함하는지 확인
        if not any(menu_word in sentence for menu_word in row['menu_name_split']):
            filtered_sentences.append(sentence)
    return filtered_sentences

""" KeyBERT """

# KeyBERT 로드. (KoBERT 사용)
model = BertModel.from_pretrained("skt/kobert-base-v1")
# KeyBERT 모델 초기화 (skt의 Kobert 사용)
kw_model = KeyBERT(model)

# keybert돌리고 키워드 리턴하는 함수 (!! -- ngram은 무조건 켜야함 -- !!)
def extract_keywords_with_candidate(document, candidate, top_n=20):
    # 주어진 리뷰들의 문장 리스트에서 각 문장별로 키워드를 추출하여 출력
    keywords = kw_model.extract_keywords(
        document,
        keyphrase_ngram_range=(1,3),  # 단어 n-gram 범위
        stop_words=None,  # 불용어
        # use_maxsum=False,
        use_mmr=True,
        diversity=0.9,  # 다양성
        top_n=top_n,
        # highlight=True,
        candidates=candidate
    )  # 상위 n개 키워드

    return keywords

def adverb_remover(text):
    results = []
    result = kiwi.analyze(text)
    for token, pos, _, len_token in result[0][0]:
        if (
            len_token != 1
            and pos.startswith("J") == False
            and pos.startswith("E") == False
            and pos.startswith("MAJ") == False
        ):
            results.append(token)
    return results

# 데이터 형식을 input text에 맞게 변환하는 함수 제작
def doc_to_input_text(review_doc):
    # 식당의 문장 리스트 추출
    input_text = ".".join(review_doc)
    input_text = adverb_remover(input_text)
    input_text=" ".join(input_text)

    return input_text

def doc_to_lda_input_text(review_doc):
    # 식당의 문장 리스트 추출
    input_text = ".".join(review_doc)
    input_text = adverb_remover(input_text)
    # input_text=" ".join(input_text)

    return list(input_text)

# df1의 각 main_menu가 어떤 카테고리에 속하는지 확인
def sub_to_org(menu, submenu_to_menu):
    for key, org_menuname in submenu_to_menu.items():
        if menu == key:
            return org_menuname
    
    return menu  # 카테고리를 찾지 못한 경우

def duplicate_removed_list(duplicated_list):
    # [[menu1, score1], [menu1, score2]]
    # 각 메뉴 항목에 대한 스코어를 저장할 defaultdict 생성
    menu_scores = defaultdict(list)

    # 데이터를 defaultdict에 저장하여 그룹화
    for menu, score in duplicated_list:
        menu_scores[menu].append(score)

    # 각 메뉴 항목의 스코어 평균을 계산
    averaged_scores = []
    for menu, scores in menu_scores.items():
        average_score = sum(scores) / len(scores)
        averaged_scores.append([menu, average_score])
    # [[menu1, avg_score1], [menu2, avg_score2]]
    
    return averaged_scores

    

""" Sentiment Penalty """

# main menu로 filtered_org_menu_dict 생성
def filter_org_menu_dict(row):
    # 문자열로 표기된 딕셔너리 실제 딕셔너리 리스트로 변환
    try:
        org_menu_dicts = ast.literal_eval(row['org_menu_dict'])
    except:
        org_menu_dicts = row['org_menu_dict']
    main_menu = row['main_menu']

    # key에 main_menu 포함하는 org_menu_dicts만 필터링
    filtered_org_menu_dicts = []
    for menu_dict in org_menu_dicts:
        for key, variations in menu_dict.items():
            if main_menu == key:
                filtered_org_menu_dicts.append(menu_dict)
                break
    
    return filtered_org_menu_dicts

# filtered_org_menu_dict로 filtered_reviews 생성
def filter_reviews_by_menu(row):
    # 리뷰 문자열을 리스트로 변환
    try:
        reviews = ast.literal_eval(row['menu_reviews'])
    except:
        reviews = row['menu_reviews']
    
    # filtered_org_menu_dict로부터 추출된 모든 메뉴(value) 추출
    menu_variations = set()
    for menu_dict in row['filtered_org_menu_dict']:
        for variations in menu_dict.values():
            menu_variations.update(variations)
    
    # menu_variations 포함하는 리뷰만 필터링

    filtered_reviews = [review for review in reviews if any(menu_variation in review for menu_variation in menu_variations)]
    
    return filtered_reviews


""" Ranking """

def assign_ranking(menu_table, sorted_data):
    try:
        menu_table['menu_id'] = menu_table['menu_id'].astype(int)
    except:
        pass
    try:
        sorted_data['menu_id'] = sorted_data['menu_id'].astype(int)
    except:
        pass

    # sorted_data에서 각 restaurant_id 별로 total_score를 기준으로 내림차순 정렬
    sorted_data['rank'] = sorted_data.groupby('restaurant_id')['total_score'].rank(ascending=False, method='dense')
    
    # ranking 컬럼을 생성/업데이트하기 위해 menu_id와 rank만 있는 임시 데이터프레임 생성
    ranking_df = sorted_data[['menu_id', 'rank']]
    
    # menu_sample 데이터프레임에 ranking 정보를 업데이트
    # menu_id를 기준으로 두 데이터프레임을 결합
    menu_table = menu_table.merge(ranking_df, on='menu_id', how='left')
    
    # 결합된 결과에서 기존의 ranking 컬럼을 새로운 rank 값으로 업데이트
    menu_table['ranking'] = menu_table['rank']
    # 임시 rank 컬럼 삭제
    menu_table.drop('rank', axis=1, inplace=True)
    
    return menu_table