import os
import random

import cv2
import imgaug as ia
import imgaug.augmenters as iaa
import numpy as np
import zerohertzLib as zz

GAP = 4
SEQ = iaa.Sequential(
    [
        # iaa.Fliplr(0.5),
        # iaa.Flipud(0.5),
        iaa.PerspectiveTransform(scale=(0, 0.03)),
        # iaa.MotionBlur(k=3, angle=[-45, 45]),
        iaa.MultiplyAndAddToBrightness(mul=(0.8, 1.2), add=(-10, 10)),
    ]
)
SYNTHETIC = ""
YOLO = {"[CLASS1]": 0, "[CLASS2]": 1}


if __name__ == "__main__":
    coco = zz.vision.CocoLoader(
        "",
        # vis_path="TMP",
        # class_color={"[CLASS1]": (255, 0, 0), "[CLASS2]": (0, 0, 255)},
    )
    sources = zz.vision.ImageLoader("sources")
    zz.util.rmtree(os.path.join(SYNTHETIC, "images"))
    zz.util.rmtree(os.path.join(SYNTHETIC, "labels"))
    cnt = 0
    while cnt < 200:
        for img, classes, bboxes, _ in coco:
            status = True
            # for cls in classes:
            #     if cls == "[CLASS2]":
            #         status = False
            #         break
            # if not status:
            #     continue
            bboxes_ = []
            for cls, box in zip(classes, bboxes):
                x0, y0, x1, y1 = zz.vision.cwh2xyxy(box)
                if cls == "[CLASS2]" or random.random() < 0.5:
                    bboxes_.append(ia.BoundingBox(x0, y0, x1, y1, cls))
                    continue
                _, src = random.choice(sources)
                x0_ = random.randrange(int(x0 - GAP), int(x0 + GAP))
                y0_ = random.randrange(int(y0 - GAP), int(y0 + GAP))
                size = int(max(box[2:]))
                size = random.randrange(int(size - GAP / 2), size + GAP)
                x1_ = x0_ + size
                y1_ = y0_ + size
                _box = [x0_, y0_, x1_, y1_]
                img = zz.vision.paste(img, src, _box, vis=False)
                bboxes_.append(
                    ia.BoundingBox(
                        min(x0, x0_),
                        min(y0, y0_),
                        max(x1, x1_),
                        max(y1, y1_),
                        "[CLASS2]",
                    )
                )
            bboxes_ = ia.BoundingBoxesOnImage(bboxes_, shape=img.shape)
            img, bboxes_ = SEQ(
                images=[cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)], bounding_boxes=bboxes_
            )
            bboxes = np.zeros((len(bboxes_), 4, 2))
            yolo_gt = []
            for idx, box in enumerate(bboxes_):
                x0, y0, x1, y1, cls = box.x1, box.y1, box.x2, box.y2, box.label
                h, w = img[0].shape[:2]
                yolo_gt.append(
                    f"{YOLO[cls] } {(x1 + x0) / 2 / w} {(y1 + y0) / 2 / h} {(x1 - x0) / w} {(y1 - y0) / h}"
                )
            cv2.imwrite(os.path.join(SYNTHETIC, "images", f"{cnt:08}.png"), img[0])
            with open(os.path.join(SYNTHETIC, "labels", f"{cnt:08}.txt"), "w") as file:
                file.writelines("\n".join(yolo_gt))
            cnt += 1
