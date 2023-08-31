import cv2
from PIL import Image


def video_to_frames(video_path, target_fps, quality):
    frames = []
    cap = cv2.VideoCapture(video_path)
    original_fps = round(cap.get(cv2.CAP_PROP_FPS))

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % (original_fps // target_fps) == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            width, height = pil_img.size
            new_width = int(width * quality / 100)
            new_height = int(height * quality / 100)
            resized_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
            frames.append(resized_img)

        frame_count += 1

    cap.release()
    return frames


def create_gif_from_frames(frames, output_filename, duration):
    frames[0].save(
        output_filename,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration,
    )


if __name__ == "__main__":
    video_path = input("VID PATH:\t")
    target_fps = int(input("Frame Per Second [FPS]:\t"))
    quality = float(input("Quality [%]:\t"))

    duration = 1000 // target_fps
    frames = video_to_frames(video_path, target_fps, quality)
    create_gif_from_frames(frames, "output.gif", duration)
