import argparse
import configparser
import os
import pandas as pd
import utils
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math


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

    all_embeddings_dict = defaultdict(list)

    # Load embeddings for each model separately
    images_dir = config["dataset"].get("images_dir")
    base_embd_dir = os.path.basename(images_dir)
    if os.path.isdir(os.path.join(args.experiment_path, base_embd_dir)):
        for dir in os.listdir(os.path.join(args.experiment_path, base_embd_dir)):
            if os.path.isdir(os.path.join(args.experiment_path, base_embd_dir, dir)):
                print(f"--- Processing images from: {dir} ---")
                for model in os.listdir(
                    os.path.join(args.experiment_path, base_embd_dir, dir)
                ):
                    embeddings_df = pd.read_csv(
                        os.path.join(
                            args.experiment_path,
                            base_embd_dir,
                            dir,
                            model,
                            "image_embeddings.csv",
                        ),
                        index_col=0,
                    )
                    all_embeddings_dict[model].append(embeddings_df)

    all_embeddings_concat = {
        key: pd.concat(value, ignore_index=False)
        for key, value in all_embeddings_dict.items()
    }

    comparison_results_dict = defaultdict(dict)

    # Loop through descriptor embeddings and compare against all embeddings
    all_descriptors = descriptor_embeddings.index.tolist()
    top_k = config["probe"].getint("top_k")
    for descriptor in all_descriptors:
        # Get the descriptor text feature embeddings
        descriptor_emb = descriptor_embeddings.loc[descriptor].values
        # Run the comparisons for each model in all_embeddings_concat
        for model, embeddings in all_embeddings_concat.items():
            images_list = embeddings.index.tolist()
            similarities = utils.scaled_dot_product(
                text_vector=descriptor_emb,
                image_array=embeddings.values,
            )[:top_k]
            top_k_img_matches = utils.match_top_k_to_images(
                similarities=similarities,
                image_list=images_list,
            )
            comparison_results_dict[descriptor][model] = top_k_img_matches
            # print(f"Descriptor: {descriptor}")
            # print(f"Model: {model}")
            # print(f"Top {top_k} image matches: {top_k_img_matches}")

    utils.plot_top_k_images(
        comparison_results_dict,
        top_k=10,
        image_base_path=images_dir,
        save_path=args.experiment_path,
    )

    # Create an empty list to store the results
    results = []

    # Iterate over each descriptor and model
    for descriptor, models in comparison_results_dict.items():
        for model, image_files in models.items():
            image_names = [file.split("_")[0] for file in image_files]
            # Count the occurrences of each name
            name_counts = pd.Series(image_names).value_counts()
            # Calculate the percentage of each name
            name_percentages = name_counts / len(image_names) * 100

            # Append the results to the list
            for name, percentage in name_percentages.items():
                results.append([descriptor, model, name, percentage])

    # Create a DataFrame from the results
    results_df = pd.DataFrame(
        results, columns=["Descriptor", "Model", "Name", "Percentage"]
    )
    # Save the results to a CSV file
    results_df.to_csv(
        os.path.join(args.experiment_path, "comparison_results.csv"), index=False
    )

    # Define a consistent color mapping for each model
    color_mapping = {
        "dalle3": "#3584bb",
        "dalle2": "#44c4d3",
        "sd21": "#f7a827",
    }

    # Calculate the number of rows and columns needed for the grid
    num_descriptors = len(results_df["Descriptor"].unique())
    num_rows = math.ceil(math.sqrt(num_descriptors))
    num_cols = math.ceil(num_descriptors / num_rows)

    # Create subplots for each descriptor in a grid layout with increased spacing
    fig = make_subplots(
        rows=num_rows,
        cols=num_cols,
        subplot_titles=results_df["Descriptor"].unique(),
        shared_yaxes=False,
        vertical_spacing=0.05,  # Increase vertical spacing
        horizontal_spacing=0.15,  # Increase horizontal spacing
    )

    # Iterate over each descriptor
    for i, descriptor in enumerate(results_df["Descriptor"].unique(), start=1):
        # Filter the data for the current descriptor
        descriptor_data = results_df[results_df["Descriptor"] == descriptor]

        # Create traces for each model
        for model in descriptor_data["Model"].unique():
            model_data = descriptor_data[descriptor_data["Model"] == model]
            fig.add_trace(
                go.Bar(
                    y=model_data["Name"],
                    x=model_data["Percentage"],
                    name=model,
                    marker_color=color_mapping[model],  # Use the consistent color
                    orientation="h",
                    showlegend=(i == 1),  # Show legend only for the first descriptor
                    width=0.30,  # Adjust the width of the bars
                ),
                row=(i - 1) // num_cols + 1,
                col=(i - 1) % num_cols + 1,
            )

    # Update the layout with larger size and better font
    fig.update_layout(
        height=800 * num_rows,  # Increase the height
        width=700 * num_cols,  # Increase the width
        showlegend=True,
        legend_title_text="Model",
        plot_bgcolor="white",
        legend=dict(
            font=dict(
                family="Helvetica Neue",  # Use the font name
                size=32,  # Increase legend font size
                color="black",
            )
        ),
        font=dict(
            family="Helvetica Neue",  # Use LaTeX-like font
            size=16,  # Increase font size
            color="black",
        ),
        title_font=dict(family="Helvetica Neue", size=18, color="black"),
    )

    # Update x-axis and y-axis labels for each subplot
    for i in range(1, num_rows * num_cols + 1):
        fig.update_xaxes(
            title_text="Proportion (%)",
            row=(i - 1) // num_cols + 1,
            col=(i - 1) % num_cols + 1,
            title_font=dict(family="Helvetica Neue", size=18),
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="grey",
            gridcolor="lightgrey",
        )

        fig.update_yaxes(
            title_font=dict(family="Helvetica Neue", size=18),
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="grey",
        )

    # Save the figure as PDF
    fig.write_image(os.path.join(args.experiment_path, "comparison_results.pdf"))


if __name__ == "__main__":
    run()
