import pandas as pd
import re
from kiwipiepy import Kiwi
import ast
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

""" 인풋 텍스트 전처리 """
def drop_short_words(df, threshold):
    # 텍스트가 없는 널값 제거
    df = df.dropna(subset=['content'])

    # 한 단어 이상인 것들만 남기기
    df.loc[:, 'word_counts'] = df['content'].apply(lambda x: len(x.split()))

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
    dropped_review_table = drop_short_words(review_table, 10)

    # 'review_text' 열에 정규 표현식 함수 적용
    dropped_review_table['content'] = dropped_review_table['content'].apply(preprocess_emoji)

    # restaurant_id로 그룹화하여 content(review_text)들을 온점 단위로 합치기
    grouped_reviews = dropped_review_table.groupby('restaurant_id')['content'].apply(lambda x: ' . '.join(x)).reset_index()

    # 새로운 데이터프레임 생성 및 문장 단위 분리해 리스트 저장
    new_df = pd.DataFrame(grouped_reviews)
    new_df['review_sentence_split'] = new_df['content'].apply(kiwi_to_sentences)

    return new_df


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


# load model
tokenizer = AutoTokenizer.from_pretrained("jaehyeong/koelectra-base-v3-generalized-sentiment-analysis")
model = AutoModelForSequenceClassification.from_pretrained("jaehyeong/koelectra-base-v3-generalized-sentiment-analysis")
sentiment_classifier = TextClassificationPipeline(tokenizer=tokenizer, model=model)

# 감성분석 함수 (0~1 사이 값으로 출력)
def get_sentiment_score(sentence):
    result = sentiment_classifier(sentence)[0]
    return result['score'] if result['label'] == '1' else 1-(result['score'])

def get_sentiment_dict(sentences):
    sentiment_dict = {}

    for sentence in sentences:
        score = get_sentiment_score(sentence)
        sentiment_dict[sentence] = score

    # sentiment_dict를 score를 기준으로 내림차순으로 정렬
    sorted_sentiment = sorted(sentiment_dict.items(), key=lambda x: x[1], reverse=True)

    # 상위 10개의 key를 선택
    top_10_keys = [item[0] for item in sorted_sentiment[:20]]

    return top_10_keys