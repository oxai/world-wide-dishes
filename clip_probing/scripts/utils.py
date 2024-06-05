import torch
from numpy.linalg import norm
import numpy as np
from numpy import dot
import matplotlib.pyplot as plt
from PIL import Image
import os
from matplotlib import font_manager


def get_device() -> torch.device:
    # If there's a GPU available...
    if torch.cuda.is_available():
        # Tell PyTorch to use the GPU.
        device = torch.device("cuda")
        print(f"There are {torch.cuda.device_count()} GPU(s) available.")
        print(f"We will use the GPU: {torch.cuda.get_device_name(0)}")
    # If not...
    else:
        print("No GPU available, using the CPU instead.")
        device = torch.device("cpu")

    return device


def scaled_dot_product(text_vector, image_array):
    image_array /= norm(image_array, axis=-1, keepdims=True)
    text_vector /= norm(text_vector, keepdims=True)
    similarities = image_array @ text_vector.T
    sorted_sims = np.argsort(-similarities.squeeze())
    return sorted_sims


def scaled_dot_product_unsorted(text_vector, image_array):
    image_array /= norm(image_array, axis=-1, keepdims=True)
    text_vector /= norm(text_vector, keepdims=True)
    similarities = image_array @ text_vector.T
    return similarities


def cosine_similarity(text_vector, image_array):
    # Normalize the text vector
    text_vector /= np.linalg.norm(text_vector)
    # Normalize each image vector in the array
    image_array /= np.linalg.norm(image_array, axis=1, keepdims=True)
    # Compute the dot product between the text vector and each image vector
    dot_products = np.dot(image_array, text_vector)
    return dot_products


def cos_sim(a, b):
    return dot(a, b) / (norm(a) * norm(b))


def match_top_k_to_images(similarities, image_list):
    matched_images = [image_list[i] for i in similarities]
    return matched_images


model_names_dict = {
    "dalle2": "Dall-E 2",
    "dalle3": "Dall-E 3",
    "sd21": "Stable Diffusion 2.1",
}


def plot_top_k_images(
    comparison_results_dict,
    top_k=10,
    image_base_path="",
    save_path="",
    custom_font="Helvetica Neue",
):
    for descriptor, models in comparison_results_dict.items():
        num_models = len(models)
        fig_height = (
            num_models * 4.5
        )  # Adjust the figure height based on the number of models
        fig_width = (
            top_k * 4
        )  # Adjust the figure width to provide more space for annotations
        # Create the plot
        fig, axes = plt.subplots(num_models, top_k, figsize=(fig_width, fig_height))

        if num_models == 1:
            axes = [axes]

        for i, (model, model_images) in enumerate(models.items()):
            for j, image_name in enumerate(model_images[-10:]):
                continent = image_name.split("_")[0]
                image_path = os.path.join(image_base_path, continent, model, image_name)
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    axes[i, j].imshow(img)
                    axes[i, j].axis("off")  # Hide the axes
                else:
                    axes[i, j].text(
                        0.5,
                        0.5,
                        "Image not found",
                        horizontalalignment="center",
                        verticalalignment="center",
                        fontname=custom_font,
                    )
                # Set the title for each image to be its file name
                axes[i, j].set_title(image_name, fontname=custom_font, fontsize=16)

            # print(f"This is the model {model}")
            # Add the model name as a label on the left side of each row
            fig.text(
                0.01,
                (i + 0.5) / num_models,
                model_names_dict[model],
                fontname=custom_font,
                fontsize=20,
                fontweight="bold",  # Make the label bold
                rotation=0,
                ha="left",
                va="center",
            )

        plt.suptitle(
            f"{descriptor}", fontname=custom_font, fontsize=30, fontweight="bold"
        )
        plt.tight_layout(
            rect=[0.1, 0, 1, 0.95], h_pad=1.0
        )  # Adjust the layout to make space for y-labels

        # Save the plot as PDF for each descriptor
        if save_path:
            descriptor_save_path = os.path.join(save_path, f"{descriptor}_output.pdf")
            plt.savefig(
                descriptor_save_path,
                format="pdf",
                # bbox_inches="tight",
            )
            plt.close()
