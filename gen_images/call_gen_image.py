import os
import time
from typing import Callable
from urllib.request import urlretrieve

import timeout_decorator
from diffusers import StableDiffusionXLPipeline, StableDiffusionPipeline
from dotenv import dotenv_values
from openai import OpenAI
import torch
import webbrowser

from retry import retry

config = dotenv_values(".env")
# Instantiate the OpenAI client
client = OpenAI(api_key=config["OPENAI_API_KEY"])

last_api_call = None


def record_exceptions(func):
    def wrapper(*args, save_path="", **kwargs):
        save_dir = os.path.dirname(save_path)
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.basename(save_path)
        with open(os.path.join(save_dir, "failed_prompts.txt"), "a") as f:
            try:
                func(*args, save_path=save_path, **kwargs)
            except Exception as e:
                print(e)
                f.write(f"{filename}\n{e}\n\n")

    return wrapper


@record_exceptions
def call_dalle(user_prompt,
               size=None,
               quality="standard",
               model="dalle2",  # dalle2 or dalle3
               n_images=1,
               n_images_per_query=None,
               sleep=None,
               save_path: str = None,
               verbose=True,
               **kwargs):
    model = {"dalle2": "dall-e-2", "dalle3": "dall-e-3"}[model]

    if n_images_per_query is None:
        n_images_per_query = 1 if model == "dall-e-3" else 5
    if sleep is None:
        sleep = 12.5 if model == "dall-e-2" else 65
    if size is None:
        size = "1024x1024" if model == "dall-e-3" else "512x512"

    gen_images = []

    @retry(tries=3, delay=10, jitter=30)
    @timeout_decorator.timeout(90)
    def call_dalle_single():
        global last_api_call
        if last_api_call is not None:
            wait_time = last_api_call + sleep - time.time()

            if wait_time > 0:
                if verbose:
                    print(f"Waiting for {wait_time} seconds")
                time.sleep(wait_time)

        last_api_call = time.time()

        response = client.images.generate(
            model=model,
            prompt=user_prompt,
            size=size,
            quality=quality,
            n=n_images_per_query,
            **kwargs
        )

        return response.data

    for i in range((n_images - 1) // n_images_per_query + 1):
        for image in call_dalle_single():
            if save_path:
                print(image.url)
                # download image from url
                urlretrieve(image.url, f"{save_path}_{len(gen_images):02d}.png")
            gen_images.append(image)
            if len(gen_images) >= n_images:
                break

    return gen_images


def call_stable_diffusion(prompt,
                          model="sdxl",
                          height=512,
                          width=512,
                          n_images=1,
                          n_images_per_query=None,
                          save_path: str = None,
                          device="cuda" if torch.cuda.is_available() else "cpu"
                          ):
    model_id = {"sdxl": "stabilityai/stable-diffusion-xl-base-1.0", "sd21": "stabilityai/stable-diffusion-2-1"}[model]
    Pipeline = StableDiffusionXLPipeline if model == "sdxl" else StableDiffusionPipeline
    if n_images_per_query is None:
        n_images_per_query = 1 if model == "sdxl" else 5

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    gen_images = []

    pipe = Pipeline.from_pretrained(model_id,
                                    torch_dtype=torch.float32,
                                    use_safetensors=True, variant="fp16").to(device)
    for i in range((n_images - 1) // n_images_per_query + 1):
        images = pipe(prompt=prompt, height=height, width=width, num_images_per_prompt=n_images_per_query).images
        for image in images:
            image.save(f"{save_path}_{len(gen_images):02d}.png")
            gen_images.append(image)
            if len(gen_images) >= n_images:
                break

    return gen_images


def call_gen_image(prompt: str, n_images: int = 1, save_path: str = None, model: str = "dalle2") -> list:
    if "dalle" in model:
        return call_dalle(prompt, model=model, n_images=n_images, save_path=save_path)
    elif "sd" in model:
        return call_stable_diffusion(prompt, model=model, n_images=n_images, save_path=save_path)
    else:
        raise ValueError(f"Model {model} not supported")


if __name__ == "__main__":
    data = call_gen_image("A painting of a cat", n_images=5)

    print(data)

    for image in data:
        webbrowser.open(image.url)
