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
parser.add_argument("--save-root", type=str, default="./outputs")
parser.add_argument('-d', '--dish-list', nargs='+', default=[])
args = parser.parse_args()

save_dir = os.path.join(args.save_root, f"selected_dishes_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
os.makedirs(save_dir, exist_ok=True)

dish_list = args.dish_list
print(dish_list)
assert len(dish_list) % 2 == 0, "Dish list must be pairs of country and local name"

models = ("dalle2", "dalle3", "sd21") if args.model == "all" else [args.model]
for model in models:
    for country, local_name in zip(dish_list[::2], dish_list[1::2]):
        prompt = (f"Generate a photograph of food from {country} called {local_name}. "
                  f"The food should be served, ready to be eaten.")

        print(model, country, local_name, prompt)
        local_name_sanitised = local_name.replace(' / ', '/').replace('/', ' or ')
        save_path = os.path.join(save_dir, country, local_name_sanitised, model, f"{country}_{local_name_sanitised}")

        data = call_gen_image(prompt,
                              model=model,
                              n_images=args.n_images,
                              save_path=save_path)
