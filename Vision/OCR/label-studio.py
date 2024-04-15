import os
import random

import cv2
import zerohertzLib as zz
from label_studio_sdk import Client

LABEL_STUDIO_URL = ""
API_TOKEN = ""
LABEL_STUDIO_PROJ = 1


def get_image(path):
    img = cv2.imread(os.path.join(""))
    return img


def sta(shape, bbox, text, id):
    original_height, original_width = shape
    x0, y0, x1, y1 = bbox.tolist()
    width = (x1 - x0) / original_width * 100
    height = (y1 - y0) / original_height * 100
    x0 = x0 / original_width * 100
    y0 = y0 / original_height * 100
    return [
        {
            "original_width": original_width,
            "original_height": original_height,
            "image_rotation": 0,
            "value": {
                "x": x0,
                "y": y0,
                "width": width,
                "height": height,
                "rotation": 0,
            },
            "id": id,
            "from_name": "bbox",
            "to_name": "image",
            "type": "rectangle",
            "origin": "manual",
        },
        {
            "original_width": original_width,
            "original_height": original_height,
            "image_rotation": 0,
            "value": {
                "x": x0,
                "y": y0,
                "width": width,
                "height": height,
                "rotation": 0,
                "labels": ["Text"],
            },
            "id": id,
            "from_name": "label",
            "to_name": "image",
            "type": "labels",
            "origin": "manual",
        },
        {
            "original_width": original_width,
            "original_height": original_height,
            "image_rotation": 0,
            "value": {
                "x": x0,
                "y": y0,
                "width": width,
                "height": height,
                "rotation": 0,
                "text": [str(text[0].decode("utf-8"))],
            },
            "id": id,
            "from_name": "transcription",
            "to_name": "image",
            "type": "textarea",
            "origin": "manual",
        },
    ]


if __name__ == "__main__":
    label_studio_client = Client(url=LABEL_STUDIO_URL, api_key=API_TOKEN)
    label_studio_proj = label_studio_client.get_project(LABEL_STUDIO_PROJ)
    data = label_studio_proj.get_labeled_tasks()
    random.shuffle(data)
    label_studio_json = []
    cli = zz.mlops.TritonClientURL("localhost", 8901)
    cnt = 0
    for data_ in data:
        try:
            path = data_["data"]["image"]
            img = get_image(path)
            file_name = os.path.basename(path)
            tmp = {
                "data": {"ocr": os.path.join("data/local-files/?d=image", file_name)},
                "annotations": [{"result": []}],
            }
            bboxes = cli("", img)["BBOX"]
            strs = cli("", img, bboxes)["STR"]
            bboxes = zz.vision.poly2xyxy(bboxes)
            for id, (bbox, str_) in enumerate(zip(bboxes, strs)):
                tmp["annotations"][0]["result"] += sta(
                    img.shape[:2], bbox, str_, id + 1
                )
            cv2.imwrite(
                os.path.join(
                    "",
                    file_name,
                ),
                img,
            )
            label_studio_json.append(tmp)
            cnt += 1
        except:
            continue
        if cnt == 200:
            break
    zz.util.write_json(label_studio_json, "tmp")
