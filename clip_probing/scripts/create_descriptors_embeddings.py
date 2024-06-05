# Read config file
# Load model
# Generate descriptor list
# Generate embeddings
# Save embeddings
import argparse
import configparser
import os
from transformers import CLIPModel, CLIPTokenizer
import pandas as pd
import json


def run():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_path", type=str, help="path where config lies")

    # Parse the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(os.path.join(args.experiment_path, "config.ini"))

    model_name = config["model"].get("model_name")
    descriptors_json_path = config["descriptors"].get("descriptors_json_path")
    with open(os.path.join(args.experiment_path, descriptors_json_path), "r") as f:
        descriptors_json = json.load(f)
    image_prompt = config["prompt"].get("image_prompt")

    model = CLIPModel.from_pretrained(model_name)
    tokenizer = CLIPTokenizer.from_pretrained(model_name)

    all_descriptors = []
    # Access the descriptors
    descriptors = descriptors_json["descriptors"]
    for descriptor in descriptors:
        for group, sentiments in descriptor.items():
            all_descriptors.extend(sentiments["positive"])
            all_descriptors.extend(sentiments["negative"])

    img_descriptions = [
        image_prompt.format(descriptor=desc) for desc in all_descriptors
    ]

    inputs = tokenizer(img_descriptions, return_tensors="pt", padding=True)
    emb = model.get_text_features(**inputs).detach().numpy().squeeze()

    descriptors_df = pd.DataFrame(emb, index=img_descriptions)
    descriptors_df.to_csv(
        os.path.join(args.experiment_path, "descriptors_embeddings.csv")
    )
    print("Descriptors embeddings saved!")


if __name__ == "__main__":
    run()
