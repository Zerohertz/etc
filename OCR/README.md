# makeDict.py

+ `dict.txt`를 읽고 Scene Text Spotting 모델이 읽어올 수 있도록 이진 파일 `dict`로 변환

# makeData.py

+ `x1`\t`y1`\t`x2`\t`y2`\t`x3`\t`y3`\t`x4`\t`y4`\t`text` 형식으로 저장된 파일을 아래와 같은 json 형식으로 변환

```python
images = [
    {
        'coco_url': '',
        'data_captured': '',
        'file_name': FILE_NAME,
        'flickr_url': '',
        'id': ID,
        'license': 0,
        'width': WIDTH,
        'height': HEIGHT
    },
    ...
]

annotations = [
    {
        'area': AREA,
        'category_id': 1,
        'id': ID,
        'image_id': IMAGE_ID,
        'iscrowd': 0,
        'bezier_pts': BEZIER_PTS, # [float]
        'rec': REC, # [int]
        'bbox': BBOX # [float]
    },
    ...
]

TrainingData = {
    'licenses': [],
    'info': {},
    'categories': [{'id': 1, 'name': 'text', 'supercategory': 'beverage', 'keypoints': ['mean', 'xmin', 'x2', 'x3', 'xmax', 'ymin', 'y2', 'y3', 'ymax', 'cross']}],
    'images': images,
    'annotations': annotations
}
```