import argparse
import configparser
import os
import pandas as pd
from collections import defaultdict
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np  # Import numpy for normalization


def extract_region(file_path):
    path_components = file_path.split(os.sep)
    try:
        index = path_components.index("all_submitted_dishes")
        return path_components[index + 2].split(", ")
    except (ValueError, IndexError):
        return None


def extract_model_name(file_path):
    path_components = file_path.split(os.sep)
    try:
        index = path_components.index("all_submitted_dishes")
        model_name = path_components[index + 1]
        return model_name
    except (ValueError, IndexError):
        return None


def calculate_weighted_cosine_sim(
    row, descriptors, sentiment_analyzer, image_prompt, descriptor_type
):
    weight = 1 if descriptor_type == "positive" else -1
    return sum(
        weight * row[image_prompt.format(descriptor=desc)]
        for desc in descriptors[descriptor_type]
    )


def calculate_region_scores(df, descriptor_group, sentiment_analyzer, image_prompt):
    # Calculate weighted cosine similarities for each dish
    weighted_cosine_sims = {
        "positive": df.apply(
            calculate_weighted_cosine_sim,
            axis=1,
            descriptors=descriptor_group,
            sentiment_analyzer=sentiment_analyzer,
            image_prompt=image_prompt,
            descriptor_type="positive",
        ),
        "negative": df.apply(
            calculate_weighted_cosine_sim,
            axis=1,
            descriptors=descriptor_group,
            sentiment_analyzer=sentiment_analyzer,
            image_prompt=image_prompt,
            descriptor_type="negative",
        ),
    }

    # Calculate the sum of weighted cosine similarities
    sum_weighted_cosine_sims = (
        weighted_cosine_sims["positive"].sum() - weighted_cosine_sims["negative"].sum()
    )

    # Normalize by the number of dishes and the number of descriptors
    num_dishes = len(df)
    num_positive_descriptors = len(descriptor_group["positive"])
    num_negative_descriptors = len(descriptor_group["negative"])

    min_possible_sum = -num_dishes * num_negative_descriptors
    max_possible_sum = num_dishes * num_positive_descriptors

    if max_possible_sum != min_possible_sum:
        normalized_cosine_sim = (
            2
            * (
                (sum_weighted_cosine_sims - min_possible_sum)
                / (max_possible_sum - min_possible_sum)
            )
            - 1
        )
    else:
        normalized_cosine_sim = 0.0

    return normalized_cosine_sim


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "experiment_path", type=str, help="Path to the experiment directory"
    )
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(os.path.join(args.experiment_path, "config.ini"))

    cosine_sims_with_descriptors = pd.read_csv(
        os.path.join(args.experiment_path, "cosine_sims_with_descriptors.csv"),
        index_col=0,
    )

    descriptors_json_path = config["descriptors"].get("descriptors_json_path")
    with open(os.path.join(args.experiment_path, descriptors_json_path), "r") as f:
        descriptors_json = json.load(f)

    image_prompt = config["prompt"].get("image_prompt")

    sentiment_analyzer = SentimentIntensityAnalyzer()

    cosine_sims_with_descriptors["regions"] = cosine_sims_with_descriptors.index.map(
        extract_region
    )
    cosine_sims_with_descriptors["model_name"] = cosine_sims_with_descriptors.index.map(
        extract_model_name
    )

    group_by_model = cosine_sims_with_descriptors.groupby("model_name")
    for model, df in group_by_model:
        expanded_rows = []
        for idx, row in df.iterrows():
            regions = row["regions"]
            if isinstance(regions, list):
                for region in regions:
                    expanded_row = row.copy()
                    expanded_row["region"] = region
                    expanded_rows.append(expanded_row)
            else:
                expanded_rows.append(row)

        expanded_df = pd.DataFrame(expanded_rows)

        for descriptor_group in descriptors_json["descriptors"]:
            descriptor_group_name = list(descriptor_group.keys())[0]
            region_scores = {}
            for region, df in expanded_df.groupby("region"):
                print(f"Processing Region: {region}")
                region_scores[region] = calculate_region_scores(
                    df,
                    descriptor_group[descriptor_group_name],
                    sentiment_analyzer,
                    image_prompt,
                )

            region_scores_df = pd.DataFrame.from_dict(
                region_scores, orient="index", columns=[descriptor_group_name]
            )
            region_scores_df.to_csv(
                os.path.join(
                    args.experiment_path,
                    f"{model}_{descriptor_group_name}_region_scores.csv",
                )
            )


if __name__ == "__main__":
    run()
