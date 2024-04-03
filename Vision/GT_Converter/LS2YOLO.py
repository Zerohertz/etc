import zerohertzLib as zz
from label_studio_sdk import Client

LABEL_STUDIO_URL = ""
API_TOKEN = ""
IMAGE_PATH = ""
PROJ_NUM = ""


if __name__ == "__main__":
    label_studio_client = Client(LABEL_STUDIO_URL, API_TOKEN)
    label_studio_project = label_studio_client.get_project(PROJ_NUM)
    label_studio_project_title = label_studio_project.params["title"]
    label_studio_annotations = label_studio_project.get_labeled_tasks()
    zz.util.write_json(label_studio_annotations, label_studio_project_title)

    zz.vision.LabelStudio(
        label_studio_project_title,
        f"{label_studio_project_title}.json",
    ).yolo("YOLO", ["[CLASS1]", "[CLASS2]"])
