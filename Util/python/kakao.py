import os
import re
from collections import defaultdict
from glob import glob

import matplotlib.pyplot as plt
import zerohertzLib as zz
from wordcloud import WordCloud

KOR = False
WIDTH = HEIGHT = 2000
COLORMAP = "prism"


def _pre_process(text, exclude="오픈채팅봇"):
    if KOR:
        chat_pattern = re.compile(
            r"^\d{4}\. \d{1,2}\. \d{1,2}\. \w{1,2} \d{1,2}:\d{2},\s(.+?)\s?:\s(.+)$"
        )
        timestamp_pattern = re.compile(
            r"^\d{4}\. \d{1,2}\. \d{1,2}\. \w{1,2} \d{1,2}:\d{2},"
        )
        join_leave_pattern = re.compile(r".+들어왔습니다\.|.+나갔습니다\.")
    else:
        chat_pattern = re.compile(
            r"^\w{3,4} \d{1,2}, \d{4} at \d{1,2}:\d{2}\s[APM]{2},\s(.+?)\s?:\s(.+)$"
        )
        timestamp_pattern = re.compile(
            r"^\w{3,4} \d{1,2}, \d{4} at \d{1,2}:\d{2}\s[APM]{2},"
        )
        join_leave_pattern = re.compile(r".+joined this chatroom|.+left the chatroom")
    lines = text.split("\n")
    parsed_messages = []
    current_message = []
    current_nickname = None
    for line in lines:
        if join_leave_pattern.search(line):
            continue
        if timestamp_pattern.match(line):
            if current_message and current_nickname != exclude:
                parsed_messages.append((current_nickname, " ".join(current_message)))
            current_message = []
            match = chat_pattern.match(line)
            if match:
                current_nickname, message = match.groups()
                if current_nickname != exclude:
                    current_message.append(message)
        else:
            if current_message:
                current_message.append(line.strip())
    if current_message and current_nickname != exclude:
        parsed_messages.append((current_nickname, " ".join(current_message)))
    return parsed_messages


def _wc_name(cnts):
    wordcloud = WordCloud(
        width=WIDTH,
        height=HEIGHT,
        background_color="white",
        colormap=COLORMAP,
        font_path=os.path.join(
            os.path.dirname(zz.plot.__file__), "fonts", "NotoSerifKR-Medium.otf"
        ),
    ).generate_from_frequencies(cnts)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    zz.plot.savefig("name")


def _wc_text(text):
    wordcloud = WordCloud(
        width=WIDTH,
        height=HEIGHT,
        background_color="white",
        colormap=COLORMAP,
        font_path=os.path.join(
            os.path.dirname(zz.plot.__file__), "fonts", "NotoSerifKR-Medium.otf"
        ),
    ).generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    zz.plot.savefig("text")


if __name__ == "__main__":
    data = []
    for path in glob("txt/*.txt"):
        with open(path, "r", encoding="utf-8") as file:
            data += _pre_process(file.read())
    cnts = defaultdict(int)
    text = []
    for _name, _text in data:
        cnts[_name] += len(_text)
        text.append(_text)
    text = " ".join(text)
    _wc_name(cnts)
    _wc_text(text)
