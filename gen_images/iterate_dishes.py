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
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--save-root", type=str, default="./outputs")
args = parser.parse_args()

wwd_path = dotenv_values(".env")["WWD_CSV_PATH"]

df = pd.read_csv(wwd_path).sort_values(by=['id'])
print(df)

save_dir = os.path.join(args.save_root, f"dishes_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
os.makedirs(save_dir, exist_ok=True)


models = ("dalle2", "dalle3", "sd21") if args.model == "all" else [args.model]
for model in models:
    for i, row in df.iterrows():
        if i < args.start:
            continue
        countries = row["countries"]
        local_name = row["local_name"]
        prompt = (f"Generate a photograph of food from {countries} called {local_name}. "
                  f"The food should be served, ready to be eaten.")

        print(row["id"], prompt, local_name)

        local_name_sanitised = local_name.replace(' / ', '/').replace('/', ' or ')
        save_path = os.path.join(save_dir, countries, local_name_sanitised, model, f"{countries}_{row['id']:03d}_{local_name_sanitised}")

        data = call_gen_image(prompt,
                              model=model,
                              n_images=args.n_images,
                              save_path=save_path)
