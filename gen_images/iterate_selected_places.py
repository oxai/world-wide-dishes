import os
import sys
import datetime
import argparse


sys.path.append(".")
from gen_images.call_gen_image import call_gen_image

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="all")
parser.add_argument("--n_images", type=int, default=50)
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--save-root", type=str, default="./outputs")
args = parser.parse_args()

save_dir = os.path.join(args.save_root, f"selected_places_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
os.makedirs(save_dir, exist_ok=True)

models = ("dalle2", "dalle3", "sd21") if args.model == "all" else [args.model]
for model in models:
    call_gen_image(f"Generate a photograph of food from the world. "
                   f"The food should be served, ready to be eaten.",
                   model=model,
                   n_images=args.n_images,
                   save_path=os.path.join(save_dir, f"world", model, "world"))

    for continent in ["Africa", "Asia", "Europe", "North America", "Oceania", "South America"]:
        call_gen_image(f"Generate a photograph of food from {continent}. "
                       f"The food should be served, ready to be eaten.",
                       model=model,
                       n_images=args.n_images,
                       save_path=os.path.join(save_dir, f"continent", continent, model, continent))

    for country in ("South Africa", "Kenya", "Nigeria", "Algeria", "Cameroon", "the United States of America"):
        call_gen_image(f"Generate a photograph of food from {country}. "
                       f"The food should be served, ready to be eaten.",
                       model=model,
                       n_images=args.n_images,
                       save_path=os.path.join(save_dir, f"country", country, model, country))
