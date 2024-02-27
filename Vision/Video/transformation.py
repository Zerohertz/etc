from glob import glob

import cv2

for vid in glob("*.mov"):
    cap = cv2.VideoCapture(vid)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("conv" + vid, fourcc, fps, (width, height))
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame[0:75, 3000:3450, :] = frame[0:75, 3000 - 450 : 3450 - 450, :]
        out.write(frame)
    cap.release()
    out.release()
