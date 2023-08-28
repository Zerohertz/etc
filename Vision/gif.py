from PIL import Image
import os

def create_gif(image_folder, output_filename, duration=500):
    """
    이미지들을 GIF로 변환

    :param image_folder: 이미지 파일들이 저장된 폴더
    :param output_filename: 출력될 GIF 파일명
    :param duration: 각 프레임에서 이미지가 표시되는 시간 (밀리초)
    """
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort()
    
    images = [Image.open(os.path.join(image_folder, image_file)) for image_file in image_files]

    images[0].save(output_filename, save_all=True, append_images=images[1:], loop=0, duration=duration)


if __name__ == "__main__":
    image_folder = input()
    output_filename = 'output.gif'
    create_gif(image_folder, output_filename)
