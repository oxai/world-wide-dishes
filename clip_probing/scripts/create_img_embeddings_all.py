import argparse
import configparser
import os
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import pandas as pd
from pathlib import Path
from tqdm import tqdm


def run():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_path", type=str, help="path where config lies")
    parser.add_argument("--images-dir", type=str, help="path to images directory")

    # Parse the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(os.path.join(args.experiment_path, "config.ini"))

    model_name = config["model"].get("model_name")
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)

    images_dir = config["dataset"].get("images_dir")
    # Load all images in the image directory
    print(f"Loading images from {images_dir}")
    if args.images_dir is not None and args.images_dir:
        images_dir = args.images_dir
    else:
        images_dir = config["dataset"].get("images_dir")

    all_images = []
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(".png"):
                file_path = os.path.join(root, file)
                all_images.append(file_path)

    print(f"Processing {len(all_images)} number of images")

    dir_images = [Image.open(img_path).convert("RGB") for img_path in tqdm(all_images)]

    inputs = processor(
        images=dir_images,
        return_tensors="pt",
        padding=True,
    )
    print(f"Embedding {len(all_images)} number of images")
    emb = model.get_image_features(**inputs).detach().numpy().squeeze()

    def extract_image_path(image_path):
        # Split the path by '/'
        path_elements = image_path.split("/")
        indices_to_check = [
            "all_submitted_dishes",
            "countries_all",
            "all_submitted_dishes_dalle3",
        ]
        for index_name in indices_to_check:
            try:
                # Find the index of the current index_name
                index = path_elements.index(index_name)

                # Extract the desired part of the path
                image_index = "/".join(path_elements[index:])

                return image_index
            except ValueError:
                # Continue checking other index names
                continue
        # Handle case when none of the specified indices are found
        return None

    dir_imge_names = [extract_image_path(img_path) for img_path in all_images]
    image_embeddings_df = pd.DataFrame(emb, index=dir_imge_names)
    image_embeddings_df.to_csv(
        os.path.join(
            args.experiment_path,
            f"image_embeddings.csv",
        )
    )


if __name__ == "__main__":
    run()
