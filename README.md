# Palette-AI-models (AI & Data)

## Description

Palette is a dating course recommendation platform for couples. <br>
This repository covers AI technologies used in Palette.

## Member

<div align="center">

| **Moonsoo Park** | **Taeho Kim** | **Seulbeen Je** |
| :------: |  :------: | :------: |
| [<img src="https://avatars.githubusercontent.com/m0onsoo" height=150 width=150> <br/> @m0onsoo](https://github.com/m0onsoo) | [<img src="https://avatars.githubusercontent.com/Taeho0818" height=150 width=150> <br/> @Taeho0818](https://github.com/Taeho0818) | [<img src="https://avatars.githubusercontent.com/powerjsv?" height=150 width=150> <br/> @powerjsv](https://github.com/powerjsv) |

</div>

## Data

- All our data was collected from [Naver Place](https://map.naver.com/p/entry/place/1359279525?c=15.00,0,0,0,dh&placePath=/home), a map and restaurant information platform.
- To this end, we developed a crawling code and collected about 350,000 pieces of data.
- The data consists of restaurant, cafe, and bar business names, categories, locations, reviews, dishes, and dish images.

## Recommendation

- [LightGCN](https://github.com/gusye1234/LightGCN-PyTorch) was used to provide recommendation results to users.
- The graph structure was adopted because it can capture overall tastes well in user records.
- Our main function, couple recommendation, inferred the recommendation results by summing each user's embeddings.
- Due to the lack of a quantitative evaluation method for both users, we conducted a survey to more than 100 random people in their 20s and received positive responses from more than 80%.
<img width="350" alt="couple" src="https://github.com/user-attachments/assets/cf8cd784-624e-43a0-a902-23c690cba74a">


## Best Dish Extraction

- Extract reliable representative dishes from reviews
- To this end, we use [KeyBERT](https://github.com/MaartenGr/KeyBERT), a keyword extraction algorithm.
- Noting that reviews reflect users' subjective feelings, we added a Sentiment Penalty to the KeyBERT score to increase the reliability of the results.
  
<img width="450" alt="kpe" src="https://github.com/user-attachments/assets/a7743047-049c-457a-a8d7-016efcf74b80">

## Review Analysis

- We used a fine-tuned T5 to summarize a large amount of restaurant reviews.
- Provides a priority sorting function for reviews of users with similar tastes as mine by calculating the similarity between user embeddings.
- This helps users make decisions.

## Deployment

- Implement model serving using FastAPI
- [Model Serving Repo](https://github.com/SJU-Capstone-DS-DayOne/Model_serving)

## Demo

![GIFMaker_me](https://github.com/user-attachments/assets/6b4867b1-f008-41ce-9435-d15384b99b96)  
You can see more details in the video below.

## Presentation

[![Video Label](https://img.youtube.com/vi/nPBuqKDOywo/sddefault.jpg)](https://www.youtube.com/watch?v=nPBuqKDOywo)

## Awards

🎉 1st palce in Creatvie Design Competition!!

<img src="https://github.com/user-attachments/assets/8f12fc84-94c9-49a4-b22d-d8aabcf863e3" width="600" height="800" />

## References

- [Naver Place](https://map.naver.com/p/entry/place)
- [LightGCN](https://github.com/gusye1234/LightGCN-PyTorch)
- [KeyBERT](https://github.com/MaartenGr/KeyBERT)
- Fine-tuned [T5](https://huggingface.co/eenzeenee/t5-base-korean-summarization)
