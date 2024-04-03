import zerohertzLib as zz

YOLO_PATH = ""


if __name__ == "__main__":
    yolo = zz.vision.YoloLoader(f"{YOLO_PATH}/images", f"{YOLO_PATH}/labels")
    yolo.labelstudio(f"image/{YOLO_PATH}", ["[CLASS1]", "[CLASS2]"], 30)
