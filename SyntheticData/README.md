# cropYOLO.py

+ Label Studio에서 관심 영역을 annotation하고 해당 정보를 `YOLO` 양식으로 export하여 준비
+ 해당 소스 (`cropYOLO.py`)를 실행하면 crop된 이미지 (관심 영역)를 저장

# makeSyntheticDataFromJson.py

+ Label Studio에서 object를 polygon으로 annotation하고 `JSON` 양식으로 export하여 준비
+ CRAFT 모델을 학습하기 위한 `JSON`과 synthetic image이 함께 저장
+ `JSON` 파일에서 `Label`이 없으면 CRAFT 모델이 학습되지 않아 실사용 불가