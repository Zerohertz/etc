import os

import zerohertzLib as zz
from notion_client import Client

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = ""

logger = zz.logging.Logger("NOTION")
notion = Client(auth=NOTION_API_KEY)


def fetch_database_items(database_id):
    results = []
    next_cursor = None
    while True:
        response = notion.databases.query(
            database_id=database_id, start_cursor=next_cursor
        )
        results.extend(response.get("results"))
        next_cursor = response.get("next_cursor")
        if not next_cursor:
            break
    logger.info(f"DB items: {len(results)}")
    return results[:1]


def fetch_page_content(page_id):
    content = ""
    next_cursor = None
    while True:
        response = notion.blocks.children.list(
            block_id=page_id, start_cursor=next_cursor
        )
        for block in response["results"]:
            logger.info(f"Page content (type): {block['type']}")
            content += extract_text_from_block(block)
        next_cursor = response.get("next_cursor")
        if not next_cursor:
            break
    return content


def extract_text_from_block(block):
    text = ""
    if block["type"] == "paragraph":
        text += (
            "".join(
                [
                    rich_text["text"]["content"]
                    for rich_text in block["paragraph"]["rich_text"]
                ]
            )
            + "\n\n"
        )
    elif block["type"] in ["heading_1", "heading_2", "heading_3"]:
        level = int(block["type"][-1])
        heading_text = "".join(
            [
                rich_text["text"]["content"]
                for rich_text in block[block["type"]]["rich_text"]
            ]
        )
        text += f"{'#' * level} {heading_text}\n\n"
    elif block["type"] in ["bulleted_list_item", "numbered_list_item"]:
        list_marker = "-" if block["type"] == "bulleted_list_item" else "1."
        list_text = "".join(
            [
                rich_text["text"]["content"]
                for rich_text in block[block["type"]]["rich_text"]
            ]
        )
        text += f"{list_marker} {list_text}\n"
    elif block["type"] == "to_do":
        checkbox = "[x]" if block["to_do"]["checked"] else "[ ]"
        to_do_text = "".join(
            [rich_text["text"]["content"] for rich_text in block["to_do"]["rich_text"]]
        )
        text += f"{checkbox} {to_do_text}\n"
    elif block["type"] == "toggle":
        toggle_text = "".join(
            [rich_text["text"]["content"] for rich_text in block["toggle"]["rich_text"]]
        )
        text += f"▼ {toggle_text}\n"
    if block.get("has_children", False):
        next_cursor = None
        while True:
            response = notion.blocks.children.list(
                block_id=block["id"], start_cursor=next_cursor
            )
            for child_block in response["results"]:
                text += extract_text_from_block(child_block)
            next_cursor = response.get("next_cursor")
            if not next_cursor:
                break
    return text


def create_prompt_from_database_items(items):
    prompts = []
    for item in items:
        title = item["properties"]["Title"]["title"][0]["text"]["content"]
        page_id = item["id"]
        content = fetch_page_content(page_id)
        prompt = f"Title: {title}\nContent:\n{content}\n"
        prompts.append(prompt)
    return prompts


if __name__ == "__main__":
    database_items = fetch_database_items(DATABASE_ID)
    prompts = create_prompt_from_database_items(database_items)
    print(prompts[0])
