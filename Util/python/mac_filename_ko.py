import os
import shutil
import sys
import unicodedata


def move(path):
    _path = "".join(unicodedata.normalize("NFC", path))
    if os.path.isdir(path):
        return
    print(f"{path}\n{_path}")
    shutil.move(path, _path)


def main():
    if len(sys.argv) == 1:
        paths = os.listdir()
    else:
        paths = [sys.argv[1]]
    for path in paths:
        move(path)


if __name__ == "__main__":
    main()
