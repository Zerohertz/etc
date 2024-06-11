import os
import random

import numpy as np
import pandas as pd
import timm
import torch
import torchvision.transforms as transforms
import zerohertzLib as zz
from PIL import Image
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


class Image2Vector:
    def __init__(self, model_name="vit_base_patch16_224"):
        self.model = timm.create_model(model_name, pretrained=True)
        self.layer = self.model.head
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    def __call__(self, path, cnt=100):
        zz.util.rmtree("runs")
        image_size = (100, 100)
        paths = zz.vision.data._get_image_paths(path)
        random.shuffle(paths)
        paths = paths[:cnt]
        images_df = pd.DataFrame(
            [os.path.basename(path).split(".") for path in paths],
            columns=["cat_id", "pid"],
        )
        images_df["impath"] = paths
        vectors = []
        images = []
        for path in tqdm(images_df["impath"]):
            with Image.open(path) as image:
                vector = self._get_vector(image)
                vectors.append(vector)
                pad = max(image.size)
                image = zz.vision.pad(np.array(image), (pad, pad))[0]
                images.append(Image.fromarray(image).resize(image_size))
        tensors = torch.stack([transforms.ToTensor()(image) for image in images])
        writer = SummaryWriter("runs/image_vectors")
        vectors = np.array(vectors)
        metadata = [
            f"""{row["cat_id"]}_{row["pid"]}""" for _, row in images_df.iterrows()
        ]
        writer.add_embedding(vectors, metadata=metadata, label_img=tensors)
        writer.close()

    @torch.no_grad()
    def _get_vector(self, image):
        image = image.convert("RGB")
        image = self.transform(image)
        batch = torch.unsqueeze(image, 0).to(self.device)
        features = self.model.forward_features(batch)
        features = features.mean(dim=1)
        return features.squeeze().cpu().numpy()


if __name__ == "__main__":
    model = Image2Vector()
    model("./", 500)
