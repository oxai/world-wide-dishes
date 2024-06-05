# Load dataset
# Load the model
import configparser
import os
import argparse
from PIL import Image
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
from transformers import BitsAndBytesConfig
import torch
import utils
import json
import pandas as pd
import csv
from tqdm import tqdm


def run():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_path", type=str, help="path where config lies")

    # Parse the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(os.path.join(args.experiment_path, "config.ini"))

    # Load all the images
    images_dir = config["dataset"].get("images_dir")
    all_images = []

    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(".png"):
                file_path = os.path.join(root, file)
                all_images.append(file_path)

    print(f"Processing {len(all_images)} number of images")

    # Load the model
    model_name = config["model"].get("model_name")
    cache_dir = config["model"].get("cache_dir")
    processor = LlavaNextProcessor.from_pretrained(model_name, cache_dir=cache_dir)
    device = utils.get_device()
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    model = LlavaNextForConditionalGeneration.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map=device,
        cache_dir=cache_dir,
        low_cpu_mem_usage=True,
    )
    model.generation_config.pad_token_ids = model.generation_config.eos_token_id

    # Load the questions
    questions_path = config["questions"].get("path")
    with open(os.path.join(args.experiment_path, questions_path), "r") as f:
        questions_json = json.load(f)

    questions = questions_json["questions"]
    prompt_format = config["model"].get("prompt_format")

    def format_prompt(question):
        if question["type"] == "multiple_choice":
            choices_str = " ".join(
                [f"{key}: {value}" for key, value in question["choices"].items()]
            )
            return prompt_format.format(
                question_template=f"Question: {question['text']}. Choices: {choices_str}. Please respond with the letter corresponding to your choice. Answer:"
            )
        elif question["type"] == "list":
            choices_str = " ".join(
                [f"{key}: {value}" for key, value in question["choices"].items()]
            )
            return prompt_format.format(
                question_template=f"Question: {question['text']}. Choices: {choices_str}. Please respond with the letter corresponding to your choice. Answer:"
            )
        elif question["type"] == "free_form":
            return prompt_format.format(
                question_template=f"Question: {question['text']}. Answer:"
            )

    # Define the CSV file path
    csv_file_path = os.path.join(args.experiment_path, "vqa_responses.csv")

    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_file_path)

    # Open the CSV file in append mode
    with open(csv_file_path, "a", newline="") as csv_file:
        csv_writer = csv.DictWriter(
            csv_file, fieldnames=["image_name", "model_response"]
        )

        # Write the header only if the file doesn't exist
        if not file_exists:
            csv_writer.writeheader()

        for image_name in tqdm(all_images):
            image = Image.open(image_name).convert("RGB")
            prompts = [format_prompt(question) for question in questions]
            images = [image] * len(prompts)
            inputs = processor(prompts, images, return_tensors="pt", padding=True).to(
                device
            )
            outputs = model.generate(**inputs, max_new_tokens=200)
            model_response = processor.batch_decode(
                outputs, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            for idx, response in enumerate(model_response):
                question = questions[idx]
                parts = response.split("[/INST]")
                answer = parts[-1].strip()
                question["model_response"] = answer
                # Write the response to the CSV file
                csv_writer.writerow(
                    {
                        "image_name": os.path.basename(image_name),
                        "model_response": json.dumps(question),
                    }
                )


if __name__ == "__main__":
    run()
