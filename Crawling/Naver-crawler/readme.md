## review-crawling.py 사용방법

! -- 이 py파일은 restaurant-crawling.py에서 얻은 음식점, 카페, 술집 csv 데이터를 바탕으로 합니다 -- !

1. 터미널을 열고 Team-Model\Crawling 경로로 들어갑니다.
2. vscode에서 176 line에 데이터를 저장했었던 그리고 앞으로도 저장할 foler_path 경로를 설정한다.
3. file_name을 원하는 지역과 음식점(카페, 술집)으로 수정한다.
4. 이 때, csv_path의 인자를 보고 파일 이름과 맞게 되는지 확인 한 번 부탁드립니다.
5. 242 line에 저장할 파일 이름도 확인 한 번 부탁하잖슴~
6. 리뷰 수집에는 상당한 시간이 걸려 여러 번 끊어 해야한다. 199 line의 for문에서 url의 인덱스를 설정해가며 수집할 구간을 지정해주자.
7. 실행 전에 save를 해주고 터미널에서 review-crawling.py를 실행한다.
8. 저장할 이름의 파일이 없다면 새로 생성하고 이미 파일이 존재한다면 이어붙인다. 따라서 위의 url 인덱스를 바꿔가며 수집해도 뒤에 잘 이어붙게 된다.