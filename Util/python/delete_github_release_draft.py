import os

import requests

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


def delete_all_draft_releases():
    """저장소의 모든 draft 릴리스를 삭제합니다."""

    releases_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"

    # 1. 모든 릴리스 정보 가져오기
    print("릴리스 목록을 가져오는 중...")
    response = requests.get(releases_url, headers=headers)

    if response.status_code != 200:
        print(
            f"오류: 릴리스 목록을 가져올 수 없습니다. (상태 코드: {response.status_code})"
        )
        print(response.json())
        return

    releases = response.json()
    draft_releases = [r for r in releases if r.get("draft")]

    if not draft_releases:
        print("삭제할 Draft 릴리스가 없습니다.")
        return

    print(f"총 {len(draft_releases)}개의 Draft 릴리스를 찾았습니다.")

    # 2. 찾은 Draft 릴리스를 순회하며 삭제
    for release in draft_releases:
        release_id = release["id"]
        release_name = release["name"]
        delete_url = (
            f"https://api.github.com/repos/{OWNER}/{REPO}/releases/{release_id}"
        )

        print(f"삭제 중: '{release_name}' (ID: {release_id})")
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code == 204:
            print("-> 성공적으로 삭제되었습니다. 🗑️")
        else:
            print(f"-> 삭제 실패! (상태 코드: {delete_response.status_code})")
            print(delete_response.json())


if __name__ == "__main__":
    delete_all_draft_releases()
