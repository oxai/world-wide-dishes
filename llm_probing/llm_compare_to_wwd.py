import argparse

import pandas as pd

import sys

import yaml
from dotenv import dotenv_values

sys.path.append(".")

from llm_probing.llm_cleanup_df import autoclean
from llm_probing.call_llm import ask_chatbot


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=str)
    parser.add_argument("--exp", "-e", type=str, default="all")
    args = parser.parse_args()

    wwd_path = dotenv_values(".env")["WWD_CSV_PATH"]
    wwd_df = pd.read_csv(wwd_path)
    llm_df = pd.read_csv(args.csv).add_suffix('_llm')

    merged_df = pd.merge(llm_df, wwd_df, left_on='id_llm', right_on='id', how='inner')
    merged_df = merged_df.drop(columns=['id_llm'])

    print(merged_df.head())
    print(merged_df.columns)

    with open("llm_probing/prompts/autocompare_columns.yaml", "r") as f:
        autocompare_config = yaml.safe_load(f)

    columns = autocompare_config.keys() if args.exp == 'all' else [args.column]

    for column in columns:
        if column in autocompare_config:
            column_config = autocompare_config[column]
            print(f"Processing {column}...")

            def apply_prompt(row):
                prompt_inputs = {c: row[c] for c in column_config["input_columns"]}
                print(prompt_inputs)
                response = ask_chatbot(column_config["prompt"].format(**prompt_inputs), column_config["return_type"])
                return str(autoclean(response, column_config["return_type"]))

            merged_df[column] = merged_df.apply(apply_prompt, axis=1)

    # rename column
    merged_df = merged_df.rename(columns={"seed_llm": "seed"})

    save_columns = {'id': True, 'local_name': True, "continent": True, "seed": True}
    for column in columns:
        save_columns[column] = True
        for c in autocompare_config[column].get("input_columns", []):
            save_columns[c] = True

    print(save_columns.keys())

    merged_df[save_columns.keys()].to_csv(args.csv.replace(".csv", "_compared.csv"), index=False)
