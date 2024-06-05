import os
import time
from urllib.request import urlretrieve

import pandas as pd
import sys
import datetime
import argparse

from dotenv import dotenv_values

sys.path.append(".")
from gen_images.call_gen_image import call_gen_image

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="all")
parser.add_argument("--n_images", type=int, default=5)
parser.add_argument("--save-root", type=str, default="./outputs")
args = parser.parse_args()

wwd_30_dishes_path = dotenv_values(".env")["WWD_30_DISHES_CSV_PATH"]

df = pd.read_csv(wwd_30_dishes_path)
print(df)

save_dir = os.path.join(args.save_root, f"selected_dishes_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
os.makedirs(save_dir, exist_ok=True)

models = ("dalle2", "dalle3", "sd21") if args.model == "all" else [args.model]
for model in models:
    for country in ("Nigeria", "Cameroon", "Algeria", "South Africa", "Kenya", "the United States of America",):
        for i, local_name in enumerate(df[country].values):
            if pd.isna(local_name) or not isinstance(local_name, str):
                continue
            prompt = (f"Generate a photograph of food from {country} called {local_name}. "
                      f"The food should be served, ready to be eaten.")

            print(country, local_name, prompt)
            local_name_sanitised = local_name.replace(' / ', '/').replace('/', ' or ')
            save_path = os.path.join(save_dir, country, local_name_sanitised, model, f"{country}_{i:03d}_{local_name_sanitised}")

            data = call_gen_image(prompt,
                                  model=model,
                                  n_images=args.n_images,
                                  save_path=save_path)
