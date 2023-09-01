import os

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


class JMY:
    def __init__(self, degree):
        self.data = pd.read_excel("data.xls")
        """
        NOTE: "벤처기업부설연구소", "중견기업부설연구소", "중소기업부설연구소"를 제외한 모든 업종은 박사 전문연구요원으로 간주
        과기원
        과기원부설연구소
        국가기관 등 연구소
        기초연구연구기관
        대기업부설연구소
        대학원연구기관
        방산연구기관
        벤처기업부설연구소
        자연계대학부설연구기관
        정부출연연구소
        중견기업부설연구소
        중소기업부설연구소
        지역혁신센터연구소
        특정연구소
        """
        self.degree = degree
        DIR_NAME = ["ALL", "MS", "PhD"]
        self.dir = DIR_NAME[degree]
        os.makedirs(self.dir, exist_ok=True)
        if degree == 1:
            self.data = self.data[
                (self.data["업종"] == "벤처기업부설연구소")
                | (self.data["업종"] == "중견기업부설연구소")
                | (self.data["업종"] == "중소기업부설연구소")
            ]
        elif degree == 2:
            self.data = self.data[
                ~(
                    (self.data["업종"] == "벤처기업부설연구소")
                    | (self.data["업종"] == "중견기업부설연구소")
                    | (self.data["업종"] == "중소기업부설연구소")
                )
            ]
        self.data["위치"] = (
            self.data["주소"]
            .str.replace("서울특별시 ", "서울특별시")
            .str.replace("경기도 ", "경기도")
            .str.split(" ")
            .str[0]
            .str.replace("서울특별시", "서울특별시 ")
            .str.replace("경기도", "경기도 ")
        )
        plt.rcParams["font.size"] = 15
        plt.rcParams["font.family"] = "Do Hyeon"

    def pie_hist(self, tar, threshold=3):
        field_counts = self.data[tar].value_counts()
        large_parts = field_counts[field_counts / len(self.data) * 100 >= threshold]
        small_parts = field_counts[field_counts / len(self.data) * 100 < threshold]
        large_parts_labels = [
            f"{i} ({v})" for i, v in zip(large_parts.index, large_parts.values)
        ]
        plt.figure(figsize=(25, 10))
        plt.subplot(1, 2, 1)
        colors = sns.color_palette("coolwarm", n_colors=len(large_parts))[::-1]
        plt.pie(
            large_parts,
            labels=large_parts_labels,
            autopct="%1.1f%%",
            startangle=90,
            radius=0.9,
            colors=colors,
        )
        plt.title(f"{threshold}% 이상 {tar} 분포", fontsize=25)
        plt.subplot(1, 2, 2)
        plt.grid(zorder=0)
        colors = sns.color_palette("Spectral", n_colors=len(large_parts))
        bars = plt.bar(
            small_parts.index,
            small_parts.values,
            color=colors[: len(small_parts)],
            zorder=2,
        )
        for bar in bars:
            height = bar.get_height()
            percentage = (height / len(self.data)) * 100
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{percentage:.1f}%",
                ha="center",
                va="bottom",
            )
        plt.xlabel(tar)
        plt.ylabel("빈도")
        plt.xticks(small_parts.index, rotation=45)
        plt.title(f"{threshold}% 미만 {tar} 분포", fontsize=25)
        plt.savefig(f"{self.dir}/{tar}.png", dpi=300, bbox_inches="tight")

    def rank_vis(self, by="현역 복무인원", top=10):
        ranked_data = self.data.sort_values(by=by, ascending=False).iloc[
            :top, [1, 14, 15, 16]
        ]
        plt.figure(figsize=(10, int(0.9 * top)))
        plt.grid(zorder=0)
        colors = sns.color_palette("coolwarm", n_colors=top)
        bars = plt.barh(
            ranked_data["업체명"][::-1],
            ranked_data[by][::-1],
            color=colors,
            zorder=2,
        )
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width,
                bar.get_y() + bar.get_height() / 4,
                f"{width}명",
                ha="right",
                va="bottom",
            )
        plt.xlabel(by)
        plt.ylabel("업체명")
        plt.title(f"{by} TOP {top}", fontsize=25)
        plt.savefig(
            f"{self.dir}/TOP_{top}_{by.replace(' ', '_')}.png",
            dpi=300,
            bbox_inches="tight",
        )

    def rank_readme(self, top=300):
        ranked_data = self.data.sort_values(by="현역 복무인원", ascending=False).iloc[
            :top, [1, 14, 15, 16]
        ]
        with open(f"{self.dir}/README.md", "w") as f:
            f.writelines(
                f"<div align=center> <h1> :technologist: 전문연구요원 TOP {top} :technologist: </h1> </div>\n\n|업체명|현역 배정인원|현역 편입인원|현역 복무인원|\n|:-:|:-:|:-:|:-:|\n"
            )
            for name, a, b, c in ranked_data.values:
                f.writelines(f"|{name}|{a}|{b}|{c}|\n")


if __name__ == "__main__":
    # NOTE: [전체 전문연구요원]
    jmy = JMY(0)
    jmy.pie_hist("연구분야", 3)
    jmy.pie_hist("지방청", 3)
    jmy.pie_hist("업종", 3)
    jmy.pie_hist("위치", 2)
    jmy.rank_vis("현역 복무인원", 30)
    jmy.rank_vis("현역 편입인원", 30)
    jmy.rank_readme()

    # NOTE: [석사 전문연구요원]
    jmy = JMY(1)
    jmy.pie_hist("연구분야", 3)
    jmy.pie_hist("지방청", 3)
    jmy.pie_hist("업종", 3)
    jmy.pie_hist("위치", 2)
    jmy.rank_vis("현역 복무인원", 30)
    jmy.rank_vis("현역 편입인원", 30)
    jmy.rank_readme()

    # NOTE: [박사 전문연구요원]
    jmy = JMY(2)
    jmy.pie_hist("연구분야", 3)
    jmy.pie_hist("지방청", 3)
    jmy.pie_hist("업종", 3)
    jmy.pie_hist("위치", 2)
    jmy.rank_vis("현역 복무인원", 30)
    jmy.rank_vis("현역 편입인원", 30)
    jmy.rank_readme()
