from glob import glob

from loguru import logger
from pydub import AudioSegment

"""
brew install ffmpeg
pip install pydub
"""


def convert_m4a_to_mp3(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file, format="m4a")
        audio.export(output_file, format="mp3")
        logger.info(f"'{input_file}'을(를) '{output_file}'로 성공적으로 변환했습니다.")
    except FileNotFoundError:
        logger.error(f"오류: '{input_file}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        logger.error(f"변환 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":

    for path in glob("*.m4a"):
        convert_m4a_to_mp3(path, path.replace(".m4a", ".mp3"))
