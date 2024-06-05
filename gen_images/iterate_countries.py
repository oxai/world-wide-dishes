import os
import time
from urllib.request import urlretrieve

import pandas as pd
import sys
import datetime
import argparse

sys.path.append(".")
from gen_images.call_gen_image import call_gen_image

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="all")
parser.add_argument("--n_images", type=int, default=5)
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--save-root", type=str, default="./outputs")
args = parser.parse_args()

df = pd.read_csv("./data/countries_with_continent.csv")
print(df)

save_dir = os.path.join(args.save_root, f"countries_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
os.makedirs(save_dir, exist_ok=True)

models = ("dalle2", "dalle3", "sd21") if args.model == "all" else [args.model]
for model in models:
    for i, row in df.iterrows():
        if i < args.start:
            continue
        country = row["country"]
        print(country)
        prompt = f"Generate a photograph of food from {country}. The food should be served, ready to be eaten."
        save_path = os.path.join(save_dir, f"{i:03d}_{country}", model, country)

        data = call_gen_image(prompt,
                              model=model,
                              n_images=args.n_images,
                              save_path=save_path)
