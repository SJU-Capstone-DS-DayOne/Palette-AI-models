import warnings
# 'UserWarning' 유형의 경고를 숨김
warnings.filterwarnings('ignore')

import nltk
# nltk.download('punkt')
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
from transformers import pipeline
from tqdm import tqdm
import os
from functions import *
import ast

tqdm.pandas()

""" Data Load """

print("=" * 10, end="")
print(" Data Load ", end="")
print("=" * 10)

path = "../data/"
restaurant = pd.read_csv(path + "restaurant_summary.csv", encoding='utf-8-sig')
# menu = pd.read_csv(path + "menu.csv", encoding='utf-8-sig')
# review = pd.read_csv(path + "review.csv", encoding='utf-8-sig')
summary_input = pd.read_csv(path + "summary_input.csv", encoding='utf-8-sig')


try:
    summary_input["review_sentence_split"] = summary_input["review_sentence_split"].apply(ast.literal_eval)
except:
    pass

try:
    summary_input["menu_name_split"] = summary_input["menu_name_split"].apply(ast.literal_eval)
except:
    pass


start = 150
end = 600

""" Input Text Preprocessing """

print("=" * 10, end="")
print(" Input Text Preprocessing ", end="")
print("=" * 10)

# rev2input = review_table2input(review)
# menu2input = make_menu_list(menu)

# summaray_input = pd.merge(rev2input, menu2input, on='restaurant_id')
# summaray_input = summaray_input[['restaurant_id', 'menu_id', 'review_sentence_split', 'menu_name_split', 'org_menu_dict']]
# summaray_input.to_csv(path + "summary_input.csv", index=False, encoding='utf-8-sig')

# summaray_input['menu_sentence'] = summaray_input.apply(filter_menu_sentences, axis=1)
# summaray_input['non_menu_sentence'] = summaray_input.apply(filter_non_menu_sentences, axis=1)

# summaray_input.loc[start:end, 'top_n_sentences'] = summaray_input.loc[start:end, 'non_menu_sentence'].progress_apply(get_sentiment_dict)

# # input text 열 만들기
# summaray_input['input_text'] = summaray_input['menu_sentence'] + summaray_input['top_n_sentences']

# pipe = pipeline("summarization", model="gangyeolkim/kobart-korean-summarizer-v2")

model = AutoModelForSeq2SeqLM.from_pretrained('eenzeenee/t5-base-korean-summarization')
tokenizer = AutoTokenizer.from_pretrained('eenzeenee/t5-base-korean-summarization')

print("=" * 10, end="")
print(" Summarizing ", end="")
print("=" * 10)
for i in tqdm(range(start, end), desc="summarize", mininterval=0.1):
    print()
    restaurant_id = summary_input.loc[i, 'restaurant_id']
    row = restaurant['restaurant_id'] == restaurant_id
    try:
        document = return_input_text(summary_input, i)

        print(f"Restaurant_{restaurant_id}:")
        print(document)
        print()

        # summarized = pipe(document)

        inputs = tokenizer(document, max_length=512, truncation=True, return_tensors="pt")
        output = model.generate(**inputs, num_beams=4, do_sample=True, min_length=64, max_length=256)
        decoded_output = tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        result = nltk.sent_tokenize(decoded_output.strip())[0]
        print("Summarized:")
        print(result)
        print()

        restaurant.loc[row, 'summary'] = result
        print('-' * 100)
    except:
        print(f"Restaurant_{restaurant_id} 스킵")
        # restaurant.loc[row, 'summary'] = None
        # row = restaurant['restaurant_id'] == restaurant_id
        # restaurant.loc[row, 'summary'] = '더 많은 리뷰가 필요합니다. 리뷰를 달아주세요!'


""" Save """
file_path = path + "restaurant_summary.csv"

restaurant.to_csv(file_path, index=False, encoding='utf-8-sig')
print("Save")