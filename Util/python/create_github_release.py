import os
import time

import requests
from packaging.version import parse as parse_version

# --- 설정 ---
OWNER = "Zerohertz"  # 사용자 이름 또는 조직 이름
REPO = "zerohertzLib"  # 저장소 이름
# ----------------


# 환경 변수에서 GitHub 토큰 가져오기
try:
    TOKEN = os.environ["GITHUB_TOKEN"]
except KeyError:
    print("오류: GITHUB_TOKEN 환경 변수를 설정해주세요.")
    exit(1)

# API 요청에 필요한 공통 헤더
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_sorted_tags():
    """저장소의 모든 태그를 페이지네이션을 처리하여 가져온 후, 버전 순으로 정렬합니다."""
    all_tags = []
    page = 1
    per_page = 100

    print("저장소에서 모든 태그를 가져오는 중 (페이지네이션 처리)...")
    while True:
        tags_url = f"https://api.github.com/repos/{OWNER}/{REPO}/tags"
        params = {"per_page": per_page, "page": page}
        response = requests.get(tags_url, headers=headers, params=params)
        response.raise_for_status()

        tags_on_page = response.json()
        if not tags_on_page:
            break

        all_tags.extend(tags_on_page)
        print(
            f"{len(tags_on_page)}개의 태그를 {page} 페이지에서 가져왔습니다. (총 {len(all_tags)}개)"
        )
        page += 1

    if not all_tags:
        return []

    # parse_version 함수를 직접 사용하여 안정적으로 정렬합니다.
    sorted_tags = sorted(all_tags, key=lambda t: parse_version(t["name"]))

    print(f"\n✅ 총 {len(sorted_tags)}개의 태그를 찾았으며, 아래 순서대로 처리합니다:")
    for i, t in enumerate(sorted_tags):
        print(f"  {i + 1:02d}. {t['name']}")

    return [t["name"] for t in sorted_tags]


def release_exists_for_tag(tag_name):
    """주어진 태그에 대한 릴리스가 이미 존재하는지 확인합니다."""
    release_url = (
        f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{tag_name}"
    )
    response = requests.get(release_url, headers=headers)
    return response.status_code == 200


def create_release_for_tag(tag_name, previous_tag_name=None):
    """지정된 태그에 대해 릴리스를 생성합니다."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"

    data = {
        "tag_name": tag_name,
        "name": tag_name,
        "generate_release_notes": True,
    }

    if previous_tag_name:
        data["previous_tag_name"] = previous_tag_name
        print(f"-> '{previous_tag_name}' 태그와 비교하여 릴리스 노트 생성 중...")
    else:
        print("-> 이전 태그가 없어, 저장소의 첫 릴리스로 생성 중...")

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        release_info = response.json()
        print(
            f"-> 릴리스가 성공적으로 생성되었습니다! ✨ (URL: {release_info['html_url']})"
        )
    else:
        print(f"-> 오류: 릴리스 생성 실패 (상태 코드: {response.status_code})")
        print(response.json())


def main():
    """모든 태그를 순회하며 릴리스가 없는 경우에만 생성합니다."""
    try:
        sorted_tags = get_sorted_tags()
        if not sorted_tags:
            print("처리할 태그가 없습니다.")
            return
    except requests.exceptions.RequestException as e:
        print(f"태그를 가져오는 중 오류 발생: {e}")
        return

    print("\n--- 릴리스 동기화 시작 ---\n")
    for i, tag_name in enumerate(sorted_tags):
        print(f"[{i + 1}/{len(sorted_tags)}] '{tag_name}' 태그 확인 중...")

        if release_exists_for_tag(tag_name):
            print("-> 이미 릴리스가 존재하므로 건너뜁니다. ✅")
        else:
            print("-> 릴리스가 존재하지 않습니다. 생성을 시작합니다. 🏗️")
            previous_tag = sorted_tags[i - 1] if i > 0 else None
            create_release_for_tag(tag_name, previous_tag)

        time.sleep(1)
        print("-" * 20)

    print("\n--- 모든 태그 확인 완료 ---")


if __name__ == "__main__":
    main()
