import argparse
from typing import List

import pandas as pd

import sys

from dotenv import dotenv_values

sys.path.append(".")

from llm_probing.call_llm import ask_true_or_false


def substr_in_text(substr_choices: List[str], text: str):
    for substr in substr_choices:
        if substr.lower() in text.lower():
            return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=str)
    args = parser.parse_args()

    wwd_path = dotenv_values(".env")["WWD_CSV_PATH"]

    llm_df = pd.read_csv(args.csv)
    wwd_df = pd.read_csv(wwd_path)
    diff_columns = wwd_df.columns.difference(llm_df.columns)
    merged_df = pd.merge(llm_df, wwd_df[["id", *diff_columns]], on='id', how='inner')

    keywords_dict = {
        "apologize": ["sorry", "apologize", "I'm afraid", "unfortunately"],
        "not known": ["not known", "not a known", "unknown", "not sure", "no idea", "no information", "no data", "I don't know", "I don't have", "not widely known", "not widely", "n\'t a known dish", "any known dish", "any specific information", "lesser-known", "not well known", "not well-known"],
        "not real": ["not real", "fictional", "fictitious", "imaginary", "not exist", "don't exist", "not a real", "made-up", "made up dish"],
        "take a guess": ["guess", "speculate", "making it up", "take a shot", "take a stab"],
    }
    result_columns = ["id", "seed", "local_name", *keywords_dict.keys(), "describe"]

    for key, keywords in keywords_dict.items():
        def check_keywords(row):
            response = substr_in_text(keywords, row["describe"])
            if response:
                print(key, row["local_name"], response, row["describe"])
            return response

        merged_df[key] = merged_df.apply(check_keywords, axis=1)

    merged_df[result_columns].to_csv(args.csv.replace(".csv", "_failures.csv"), index=False)
