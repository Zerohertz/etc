import os
import shutil

TARGET = {"2": "0", "3": "1"}

if __name__ == "__main__":
    ROOT = input("[ROOT]:\t")
    ORG_IMAGES_PATH = os.path.join(ROOT, "images")
    ORG_LABELS_PATH = os.path.join(ROOT, "labels")
    ORG_IMAGES = os.listdir(ORG_IMAGES_PATH)

    CONVERTED = os.path.join(ROOT, "CONVERTED")
    try:
        shutil.rmtree(CONVERTED)
    except:
        pass
    os.makedirs(CONVERTED, exist_ok=True)
    CONVERTED_IMAGES_PATH = os.path.join(CONVERTED, "images")
    CONVERTED_LABELS_PATH = os.path.join(CONVERTED, "labels")
    os.makedirs(CONVERTED_IMAGES_PATH, exist_ok=True)
    os.makedirs(CONVERTED_LABELS_PATH, exist_ok=True)

    for img in ORG_IMAGES:
        FLAG = False
        name = ".".join(img.split(".")[:-1])
        ext = img.split(".")[-1]
        with open(os.path.join(ORG_LABELS_PATH, name + ".txt"), "r") as f:
            tmp = f.readlines()
        NEW = []
        for t in tmp:
            if t[0] in TARGET.keys():
                t = TARGET[t[0]] + t[1:]
                NEW.append(t)
        if not NEW == []:
            with open(os.path.join(CONVERTED_LABELS_PATH, name + ".txt"), "w") as f:
                f.writelines(NEW)
            shutil.copy(
                os.path.join(ORG_IMAGES_PATH, img),
                os.path.join(CONVERTED_IMAGES_PATH, f"{name}.{ext}"),
            )
