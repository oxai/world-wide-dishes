import argparse
import configparser
import os
import pandas as pd
import utils
from collections import defaultdict


def run():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_path", type=str, help="path where config lies")

    # Parse the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(os.path.join(args.experiment_path, "config.ini"))

    # Load the descriptor embeddings
    descriptor_embeddings = pd.read_csv(
        os.path.join(args.experiment_path, "descriptors_embeddings.csv"), index_col=0
    )
    all_image_embeddings = pd.read_csv(
        os.path.join(args.experiment_path, "image_embeddings.csv"), index_col=0
    )
    # Loop through descriptor embeddings and compare against all embeddings
    all_descriptors = descriptor_embeddings.index.tolist()
    comparison_results_dict = defaultdict(dict)
    for descriptor in all_descriptors:
        # Get the descriptor text feature embeddings
        descriptor_emb = descriptor_embeddings.loc[descriptor].values
        # Calculate the cosine similarity between the descriptor and all images
        image_embeddings = all_image_embeddings.values
        cosin_sims = utils.cosine_similarity(descriptor_emb, image_embeddings)
        comparison_results_dict[descriptor] = cosin_sims

    # Save the comparison results
    comparison_results_df = pd.DataFrame(
        comparison_results_dict, index=all_image_embeddings.index
    )

    comparison_results_df.to_csv(
        os.path.join(args.experiment_path, "cosine_sims_with_descriptors.csv")
    )


if __name__ == "__main__":
    run()
