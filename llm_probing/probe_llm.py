import argparse
import os
from datetime import datetime

import yaml
import pandas as pd

import sys

from dotenv import dotenv_values

sys.path.append(".")
from llm_probing.call_llm import call_chatbot


def query_model_for_dish_info(prompts, model="gpt35", n=1, verbose=True, **meta_data):
    results = [{**meta_data, "seed": i} for i in range(n)]
    init_prompt = prompts["initial_prompt"].format(**meta_data)
    for prompt in prompts["questions"]:
        question = prompt["question"].format(**meta_data)
        if "multiple_choices" in prompt:
            question += ' Choose from the following: ["' + '", "'.join(
                prompt['multiple_choices']) + '"] and return as a python list of strings. You may choose multiple options. Reply with just the list.'
        elif "single_choice" in prompt:
            question += ' Choose from the following: ["' + '", "'.join(prompt['single_choice']) + '"]. You may only choose one option. Reply with just your choice.'
        if prompt.get("details", False):
            question += ' Return the answer in a python dictionary format: {"answer": "your answer here", "details": "any additional information"}. Reply with just the dictionary.'
        answers = call_chatbot([init_prompt, question], model=model, n=n)
        if verbose:
            print(question, answers)
        for i in range(n):
            results[i][prompt["key"]] = answers[i]
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="gpt35")
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--save-root", type=str, default="./outputs")
    args = parser.parse_args()

    with open("llm_probing/prompts/llm_probing.yaml", "r") as f:
        prompts = yaml.safe_load(f)

    wwd_path = dotenv_values(".env")["WWD_CSV_PATH"]

    df = pd.read_csv(wwd_path)
    print(df)
    if args.resume is not None:
        resume_df = pd.read_csv(args.resume)
        results = resume_df.to_dict(orient="records")
    else:
        resume_df = None
        results = []

    save_path = os.path.join(args.save_root, f"llm_probing_{args.model}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")

    for i, row in df.iterrows():
        if args.resume is not None and row["id"] in resume_df["id"].values:
            print(i, row["id"], row["local_name"])
            continue
        results += query_model_for_dish_info(prompts, n=args.n, model=args.model,
                                             id=row["id"], local_name=row["local_name"], country_gt=row["countries"])
        if i % 20 == 0:
            df = pd.DataFrame(results)
            print(df)
            df.to_csv(save_path, index=False)
    # convert dictionary to a pandas dataframe
    df = pd.DataFrame(results)
    print(df)
    df.to_csv(save_path, index=False)
