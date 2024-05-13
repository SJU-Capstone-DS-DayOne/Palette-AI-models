import warnings
# 'UserWarning' 유형의 경고를 숨김
warnings.filterwarnings('ignore')

import nltk
# nltk.download('punkt')
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
from transformers import pipeline
from tqdm import tqdm
from functions import *

""" Data Load """

print("=" * 10, end="")
print(" Data Load ", end="")
print("=" * 10)

path = "../data/"
restaurant = pd.read_csv(path + "restaurant.csv", encoding='utf-8-sig')
menu = pd.read_csv(path + "menu_sample.csv", encoding='utf-8-sig')
review = pd.read_csv(path + "review_sample.csv", encoding='utf-8-sig')



""" Input Text Preprocessing """

print("=" * 10, end="")
print(" Input Text Preprocessing ", end="")
print("=" * 10)

rev2input = review_table2input(review)
menu2input = make_menu_list(menu)

summaray_input = pd.merge(rev2input, menu2input, on='restaurant_id')
summaray_input = summaray_input[['restaurant_id', 'menu_id', 'review_sentence_split', 'menu_name_split', 'org_menu_dict']]


summaray_input['menu_sentence'] = summaray_input.apply(filter_menu_sentences, axis=1)
summaray_input['non_menu_sentence'] = summaray_input.apply(filter_non_menu_sentences, axis=1)

summaray_input.loc[:5, 'top_10_sentences'] = summaray_input.loc[:5, 'non_menu_sentence'].apply(get_sentiment_dict)

# input text 열 만들기
summaray_input['input_text'] = summaray_input['menu_sentence'] + summaray_input['top_10_sentences']

# pipe = pipeline("summarization", model="gangyeolkim/kobart-korean-summarizer-v2")

model = AutoModelForSeq2SeqLM.from_pretrained('eenzeenee/t5-base-korean-summarization')
tokenizer = AutoTokenizer.from_pretrained('eenzeenee/t5-base-korean-summarization')

for i in tqdm(range(len(summaray_input[:5])), desc="summarize", mininterval=0.1):
    try:
        document = '. '.join(summaray_input.loc[i, 'input_text'])
        print()
        print("Document:")
        print(document)
        print()

        # summarized = pipe(document)

        inputs = tokenizer(document, max_length=512, truncation=True, return_tensors="pt")
        output = model.generate(**inputs, num_beams=4, do_sample=True, min_length=50, max_length=256)
        decoded_output = tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        result = nltk.sent_tokenize(decoded_output.strip())[0]
        print("Summarized:")
        # print(summarized[0]["summary_text"])
        print(result)
        print()

        print('-' * 30)
    except:
        print(f"{i} 번째 스킵")