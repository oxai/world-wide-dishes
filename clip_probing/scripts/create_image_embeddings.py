import argparse
import configparser
import os
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import pandas as pd
from pathlib import Path


def run():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_path", type=str, help="path where config lies")

    # Parse the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(os.path.join(args.experiment_path, "config.ini"))

    model_name = config["model"].get("model_name")
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)

    images_dir = config["dataset"].get("images_dir")
    for top_level in os.listdir(images_dir):
        if os.path.isdir(os.path.join(images_dir, top_level)):
            print(f"========== Processing images from: {top_level} ==========")
            for dir in os.listdir(os.path.join(images_dir, top_level)):
                if os.path.isdir(os.path.join(images_dir, top_level, dir)):
                    print(f"--- Processing images from: {dir} ---")
                    dir_imge_names = os.listdir(
                        os.path.join(images_dir, top_level, dir)
                    )
                    dir_images = [
                        Image.open(
                            os.path.join(images_dir, top_level, dir, img_name)
                        ).convert("RGB")
                        for img_name in dir_imge_names
                    ]
                    inputs = processor(
                        images=dir_images,
                        return_tensors="pt",
                        padding=True,
                    )
                    emb = model.get_image_features(**inputs).detach().numpy().squeeze()

                    image_embeddings_df = pd.DataFrame(emb, index=dir_imge_names)
                    save_path = os.path.join(
                        args.experiment_path,
                        os.path.basename(images_dir),
                        top_level,
                        dir,
                    )
                    Path(save_path).mkdir(parents=True, exist_ok=True)
                    image_embeddings_df.to_csv(
                        os.path.join(
                            save_path,
                            f"image_embeddings.csv",
                        )
                    )


if __name__ == "__main__":
    run()
