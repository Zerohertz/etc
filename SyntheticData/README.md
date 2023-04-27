# cropYOLO.py

+ Label Studio에서 관심 영역을 annotation하고 해당 정보를 `YOLO` 양식으로 export하여 준비
+ 해당 소스 (`cropYOLO.py`)를 실행하면 crop된 이미지 (관심 영역)를 저장

# Make Synthetic Data

> 도면 사이 회전된 숫자의 CRAFT 모델 기반 STD를 위해서 Synthetic Data 생성

## CRAFT/Legacy/makeSyntheticDataFromJson.py

+ Label Studio에서 object를 polygon으로 annotation하고 `JSON` 양식으로 export하여 준비
+ CRAFT 모델을 학습하기 위한 `JSON`과 synthetic image이 함께 저장
+ `JSON` 파일에서 `label`이 없으면 CRAFT 모델이 학습되지 않아 실사용 불가

## CRAFT/makeSyntheticDataFromNUM.py

+ 위 코드에서 ground truth인 텍스트의 `label`이 존재하지 않기 때문에 기존 데이터의 `label`이 될 수 있는 텍스트 영역을 모두 삭제
+ 이후 이미지를 새로운 이미지에 붙이고 회전하여 랜덤한 숫자 텍스트를 삽입하고 다시 반대 방향으로 회전하여 최종적인 synthetic data 생성