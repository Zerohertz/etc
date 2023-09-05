import json
import os
import shutil
from urllib.parse import unquote

LABEL_CONVERTER = {}


def convert_rectangle_to_polygon(label_studio_json):
    STATUS = False
    labelme_json = {"shapes": []}
    annotations = label_studio_json.get("annotations", [])
    for annotation in annotations:
        results = annotation.get("result", [])
        for result in results:
            shape_type = result.get("type")
            value = result.get("value")
            ow, oh = result.get("original_width"), result.get("original_height")
            if shape_type == "rectanglelabels":
                x = value.get("x") / 100 * ow
                y = value.get("y") / 100 * oh
                width = value.get("width") / 100 * ow
                height = value.get("height") / 100 * oh
                points = [
                    [x, y],
                    [x + width, y],
                    [x + width, y + height],
                    [x, y + height],
                ]
                try:
                    label = LABEL_CONVERTER[value.get("rectanglelabels")[0]]
                    STATUS = True
                except:
                    continue
                labelme_shape = {
                    "label": label,
                    "points": points,
                    "shape_type": "polygon",
                }
                labelme_json["shapes"].append(labelme_shape)
    return labelme_json, STATUS


if __name__ == "__main__":
    TARGET_JSON_PATH = input("PATH:\t")
    TARGET_PATH = "/".join(TARGET_JSON_PATH.split("/")[:-1]) + "/labelme"
    os.makedirs(TARGET_PATH, exist_ok=True)
    TARGET_IMAGE_PATH = "/".join(TARGET_JSON_PATH.split("/")[:-1]) + "/images"
    with open(
        TARGET_JSON_PATH,
        "r",
    ) as f:
        label_studio_data = json.load(f)

    for lsd in label_studio_data:
        labelme_data, STATUS = convert_rectangle_to_polygon(lsd)
        if STATUS:
            lmf = ".".join(unquote(lsd["data"]["image"]).split("/")[-1].split(".")[:-1])
            with open(f"{TARGET_PATH}/{lmf}.json", "w") as f:
                json.dump(labelme_data, f, indent=4)
            shutil.copy(
                TARGET_IMAGE_PATH + "/" + unquote(lsd["data"]["image"]).split("/")[-1],
                TARGET_PATH,
            )
