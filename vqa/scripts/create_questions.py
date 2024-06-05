# Load dataset
# Load the model
import configparser
import os
import argparse
from PIL import Image
import json
import pandas as pd
import jsonlines
from tqdm import tqdm


def run():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_path", type=str, help="path where config lies")
    parser.add_argument("--question-file", type=str)
    parser.add_argument(
        "--questions-output-file", type=str, default="vqa_questions.jsonl"
    )
    parser.add_argument("--images-dir", type=str, help="path to images directory")

    # Parse the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(os.path.join(args.experiment_path, "config.ini"))

    # Load all the images
    if args.images_dir is not None and args.images_dir:
        images_dir = args.images_dir
    else:
        images_dir = config["dataset"].get("images_dir")

    all_images = []
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(".png"):
                file_path = os.path.join(root, file)
                all_images.append(file_path)

    print(f"Processing {len(all_images)} number of images")

    with open(args.question_file, "r") as f:
        questions_json = json.load(f)

    questions = questions_json["questions"]

    def format_prompt(question):
        if question["type"] == "multiple_choice":
            choices_str = " ".join(
                [f"{key}: {value}" for key, value in question["choices"].items()]
            )
            return f"Question: {question['text']}. Choices: {choices_str}. Please respond with the letter corresponding to your choice. Answer:"
        elif question["type"] == "list":
            choices_str = " ".join(
                [f"{key}: {value}" for key, value in question["choices"].items()]
            )
            return f"Question: {question['text']}. Choices: {choices_str}. Please respond with the letter corresponding to your choice. Answer:"
        elif question["type"] == "free_form":
            return f"Question: {question['text']}. Answer:"

    # Define the JSONL file path
    json_file_path = os.path.join(args.experiment_path, args.questions_output_file)

    # Open the JSONL file in append mode
    with jsonlines.open(json_file_path, mode="a") as writer:
        question_counter = 0
        for image_name in tqdm(all_images):
            for question in questions:
                formatted_question = format_prompt(question)
                json_question = {
                    "image_name": os.path.basename(image_name),
                    "question_id": question_counter,
                    "question": formatted_question,
                    "image_path": image_name,
                }
                writer.write(json_question)
                question_counter += 1


if __name__ == "__main__":
    run()
