import argparse
from typing import List, Dict

import numpy as np
import pandas as pd
from dotenv import dotenv_values

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=str)
    args = parser.parse_args()

    wwd_path = dotenv_values(".env")["WWD_CSV_PATH"]

    compared_df = pd.read_csv(args.csv.replace(".csv", "_compared.csv"))
    cleaned_df = pd.read_csv(args.csv).add_suffix("_llm")
    failures_df = pd.read_csv(args.csv.replace("_cleaned.csv", "_failures.csv"))
    wwd_df = pd.read_csv(wwd_path)
    diff_columns = wwd_df.columns.difference(compared_df.columns)
    merged_df = pd.merge(compared_df, wwd_df[["id", *diff_columns]], on='id', how='inner')
    diff_columns = cleaned_df.columns.difference(merged_df.columns)
    merged_df = pd.merge(merged_df, cleaned_df[diff_columns], left_on=["id", "seed"], right_on=["id_llm", "seed_llm"], how='inner')
    diff_columns = failures_df.columns.difference(merged_df.columns)
    merged_df = pd.merge(merged_df, failures_df[["id", "seed", *diff_columns]], on=["id", "seed"], how='inner')
    print(merged_df.head())
    print(merged_df.columns)


    def substr_in_text(substr_choices: List[str], text: str):
        for substr in substr_choices:
            if substr in text:
                return True
        return False


    def calc_iou(left: str, right: str, options: List[str], variations: Dict[str, str] = None):
        if variations is None:
            variations = {}
        intersect = 0
        union = 0
        options = [o.lower() for o in options]
        for option in options:
            in_left = substr_in_text([option, variations[option]] if option in variations else [option], left.lower())
            in_right = substr_in_text([option, variations[option]] if option in variations else [option], right.lower())
            if in_left and in_right:
                intersect += 1
            if in_left or in_right:
                union += 1
        return 0 if intersect == 0 else intersect / union


    def apply_iou_to_row(row, column1, column2, options, variations=None):
        try:
            return calc_iou(str(row[column1]), str(row[column2]), options, variations=variations)
        except Exception as e:
            print("***************************")
            print(e, row[column1], row[column2])
            print("***************************")
            return 0

    def apply_iou_to_df(df, pred_column_name, gt_column_name, options):
        df[f"{gt_column_name}_iou"] = df.apply(lambda row: apply_iou_to_row(row, column1=pred_column_name, column2=gt_column_name, options=options), axis=1)
        df[f"{gt_column_name}_valid_gt"] = df[gt_column_name].apply(lambda text: substr_in_text(options, str(text)))


    options = ["breakfast", "lunch", "dinner", "snack", "anytime"]
    apply_iou_to_df(merged_df, "time_of_day_llm", "time_of_day", options)

    options = ["Starter", "Soup", "Salad", "Sauce", "Side dish", "Main dish - stand alone",
               "Main dish - eaten with sides", "Small plate / bowl for sharing",
               "Small plate / bowl served as a part of a collection", "Dessert"]

    apply_iou_to_df(merged_df, "type_of_dish_llm", "type_of_dish", options)

    options = ["fork", "knife", "spoon", "chopsticks", "finger", "hand"]
    apply_iou_to_df(merged_df, "utensils_llm", "utensils", options)

    merged_df["ingredients_iou"] = merged_df.apply(lambda row: len(eval(str(row["ingredients_intersect"]))) / len(eval(str(row["ingredients_union"]))), axis=1)

    experiments = ["count", "country_acc", "time_of_day_iou", "type_of_dish_iou", "utensils_iou", "ingredients_iou", "apologize", "not known", "not real", "take a guess"]
    result_columns = ["country_match", "country_llm", "countries",
                      "time_of_day_iou", "time_of_day_llm", "time_of_day",
                      "type_of_dish_iou", "type_of_dish_llm", "type_of_dish", "utensils_iou", "utensils_llm", "utensils", "ingredients_iou", "ingredients_intersect", "ingredients_union"]

    all_results = {}
    for continent in ("Africa", "Asia", "Europe", "North America", "Oceania", "South America"):
        continent_df = merged_df[merged_df["continent"].apply(lambda x: continent in x)]
        count = len(continent_df)
        print(continent, count)
        results = []
        for experiment in experiments:
            result = None
            if experiment == "count":
                result = count
            elif experiment == "country_acc":
                result = np.mean(continent_df["country_match"])
            elif experiment == "time_of_day_iou":
                result = np.sum(continent_df["time_of_day_iou"]) / np.sum(continent_df["time_of_day_valid_gt"])
            elif experiment == "type_of_dish_iou":
                result = np.sum(continent_df["type_of_dish_iou"]) / np.sum(continent_df["type_of_dish_valid_gt"])
            elif experiment == "utensils_iou":
                result = np.sum(continent_df["utensils_iou"]) / np.sum(continent_df["utensils_valid_gt"])
            elif experiment == "ingredients_iou":
                result = np.mean(continent_df["ingredients_iou"])
            elif experiment in ("apologize", "not known", "not real", "take a guess"):
                result = np.mean(continent_df[experiment]) * 100

            if isinstance(result, float):
                result = round(result, 2)

            results.append(result)

        all_results[continent] = results

    merged_df[result_columns].to_csv(args.csv.replace(".csv", "_results.csv"), index=False)
    pd.DataFrame(all_results, index=experiments).to_csv(args.csv.replace(".csv", "_stats.csv"), index=True)
