import json
import os
import time

import requests
from loguru import logger

# --- 설정 ---
USERNAME = "Zerohertz"
GRAPHQL_URL = "https://api.github.com/graphql"
OUTPUT_FILE = "github_stars.json"
MAX_RETRIES = 5
RETRY_DELAY = 2
PAGE_SIZE = 30
REQUEST_DELAY = 0.5
# ----------------

# 환경 변수에서 GitHub 토큰 가져오기
try:
    TOKEN = os.environ["GITHUB_TOKEN"]
except KeyError:
    logger.error("GITHUB_TOKEN 환경 변수를 설정해주세요.")
    exit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def run_graphql_query(query, variables=None):
    """GraphQL query를 실행하고 결과를 반환합니다."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                raise Exception(f"GraphQL 오류: {result['errors']}")

            return result["data"]
        except requests.exceptions.HTTPError as e:
            if response.status_code in (502, 503, 504):
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (2**attempt)
                    logger.warning(
                        f"{response.status_code} 오류 발생, {delay}초 후 재시도... "
                        f"({attempt + 1}/{MAX_RETRIES})"
                    )
                    time.sleep(delay)
                    continue
            raise e

    raise Exception(f"최대 재시도 횟수 ({MAX_RETRIES}) 초과")


def get_user_lists():
    """사용자의 모든 Star Lists와 각 list에 포함된 repository를 가져옵니다."""
    query = f"""
    query($username: String!, $cursor: String) {{
        user(login: $username) {{
            lists(first: {PAGE_SIZE}, after: $cursor) {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    id
                    name
                    items(first: {PAGE_SIZE}) {{
                        pageInfo {{
                            hasNextPage
                            endCursor
                        }}
                        nodes {{
                            ... on Repository {{
                                nameWithOwner
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    """

    all_lists = {}
    cursor = None

    logger.info("Star Lists 가져오는 중...")
    while True:
        data = run_graphql_query(query, {"username": USERNAME, "cursor": cursor})
        lists_data = data["user"]["lists"]

        for list_node in lists_data["nodes"]:
            list_name = list_node["name"]
            list_id = list_node["id"]
            repos = [
                item["nameWithOwner"]
                for item in list_node["items"]["nodes"]
                if item.get("nameWithOwner")
            ]

            # 리스트 내 추가 페이지가 있는 경우 처리
            if list_node["items"]["pageInfo"]["hasNextPage"]:
                repos.extend(
                    get_list_items(list_id, list_node["items"]["pageInfo"]["endCursor"])
                )

            all_lists[list_name] = repos

        if not lists_data["pageInfo"]["hasNextPage"]:
            break
        cursor = lists_data["pageInfo"]["endCursor"]
        time.sleep(REQUEST_DELAY)

    return all_lists


def get_list_items(list_id, cursor):
    """특정 list의 추가 item들을 페이지네이션으로 가져옵니다."""
    query = f"""
    query($listId: ID!, $cursor: String) {{
        node(id: $listId) {{
            ... on UserList {{
                items(first: {PAGE_SIZE}, after: $cursor) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        ... on Repository {{
                            nameWithOwner
                        }}
                    }}
                }}
            }}
        }}
    }}
    """

    repos = []
    while cursor:
        data = run_graphql_query(query, {"listId": list_id, "cursor": cursor})
        items_data = data["node"]["items"]

        repos.extend(
            [
                item["nameWithOwner"]
                for item in items_data["nodes"]
                if item.get("nameWithOwner")
            ]
        )

        if items_data["pageInfo"]["hasNextPage"]:
            cursor = items_data["pageInfo"]["endCursor"]
            time.sleep(REQUEST_DELAY)
        else:
            break

    return repos


def get_all_starred_repos():
    """사용자의 모든 starred repository를 가져옵니다."""
    query = f"""
    query($username: String!, $cursor: String) {{
        user(login: $username) {{
            starredRepositories(first: {PAGE_SIZE}, after: $cursor) {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    nameWithOwner
                }}
            }}
        }}
    }}
    """

    all_repos = []
    cursor = None

    logger.info("Starred repository 가져오는 중...")
    while True:
        data = run_graphql_query(query, {"username": USERNAME, "cursor": cursor})
        starred_data = data["user"]["starredRepositories"]

        all_repos.extend([repo["nameWithOwner"] for repo in starred_data["nodes"]])
        logger.debug(f"{len(all_repos)}개 로드됨...")

        if not starred_data["pageInfo"]["hasNextPage"]:
            break
        cursor = starred_data["pageInfo"]["endCursor"]
        time.sleep(REQUEST_DELAY)

    return all_repos


def build_repo_to_lists_mapping(lists_data, all_starred):
    """Repository별 소속 list 매핑을 생성합니다."""
    # 리스트에 포함된 모든 repo 수집
    repos_in_lists = set()
    for repos in lists_data.values():
        repos_in_lists.update(repos)

    # repo -> lists 매핑 생성
    repo_to_lists = {}
    for list_name, repos in lists_data.items():
        for repo in repos:
            if repo not in repo_to_lists:
                repo_to_lists[repo] = []
            repo_to_lists[repo].append(list_name)

    # 리스트에 포함되지 않은 starred repo 처리
    no_list_repos = [repo for repo in all_starred if repo not in repos_in_lists]
    if no_list_repos:
        repo_to_lists["No List"] = no_list_repos

    return repo_to_lists


def main():
    """Star Lists 정보를 수집하고 JSON으로 저장합니다."""
    try:
        # Star Lists와 starred repos 모두 수집
        lists_data = get_user_lists()
        all_starred = get_all_starred_repos()

        logger.info(f"총 {len(lists_data)}개의 Lists 발견")
        logger.info(f"총 {len(all_starred)}개의 Starred repository 발견")

        # 매핑 생성
        result = build_repo_to_lists_mapping(lists_data, all_starred)

        # JSON 저장
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.success(f"결과가 '{OUTPUT_FILE}'에 저장되었습니다.")

        # 요약 출력
        no_list_count = len(result.get("No List", []))
        categorized_count = len(result) - (1 if "No List" in result else 0)
        logger.info(f"리스트에 포함된 repository: {categorized_count}개")
        logger.info(f"리스트에 포함되지 않은 repository: {no_list_count}개")

    except requests.exceptions.RequestException as e:
        logger.error(f"API 요청 중 오류 발생: {e}")
    except Exception as e:
        logger.error(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
