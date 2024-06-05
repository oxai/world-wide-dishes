# You are what you eat? Feeding foundation models a regionally diverse food dataset of World Wide Dishes
[Jabez Magomere](https://github.com/JabezNzomo99), [Shu Ishida](https://github.com/shuishida), [Tejumade Afonja](https://github.com/tejuafonja), [Aya Salama](https://github.com/Aya-S), [Daniel Kochin](https://github.com/danielkochin), [Foutse Yuehgoh](https://github.com/Foutse), [Imane Hamzaoui](https://github.com/imanehmz), [Raesetje Sefala](https://github.com/sefalab), [Aisha Aalagib](https://github.com/AishaAlaagib), [Elizaveta Semenova](https://github.com/elizavetasemenova), [Lauren Crais](https://www.law.ox.ac.uk/people/lauren-crais), [Siobhan Mackenzie Hall](https://github.com/smhall97)

Official Website (used for data collection): https://worldwidedishes.com/

## The World Wide Dishes Dataset

- [Licence and terms of use](./LICENCE.md)

We present the World Wide Dishes dataset which seeks to assess these disparities through a39
decentralised data collection effort to gather perspectives directly from people with a wide variety of40
backgrounds from around the globe with the aim of creating a dataset consisting of their insights into41
their own experiences of foods relevant to their cultural, regional, national, or ethnic lives.

- [World Wide Dishes csv](./data/WorldWideDishes_2024_June_World_Wide_Dishes.csv)
- [World Wide Dishes Excel Sheet](./data/WorldWideDishes_2024_June.xlsx)

The meta data of the World Wide Dishes dataset is available in the [Croissant format](https://github.com/mlcommons/croissant):
- [World Wide Dishes Croissant metadata](./croissant-worldwidedishes.json)

## The World Wide Dishes website
Link to the website used during data collection: <https://worldwidedishes.com/>

The website includes our Data Protection Policy and FAQs developed to support contributors during the data collection process. 

### Running your own instance of the website:

Please refer to the README.md in the webapp directory for instructions on how to run your own instance of the website.
- [Web application source code and README.md](./webapp)

## The World Wide Dishes Experiments
In addition to World Wide Dishes, we present US was selected as a baseline, and an additional test suite was curated253
for regional parity. 

- [Dishes selected for the five African countries + the US](./data/WorldWideDishes_2024_June_Selected_Countries.csv)
- [US Test set csv](./data/WorldWideDishes_2024_June_US_Test_Set.csv) (same set of dishes in the previous sheet, but also includes a regional label)
- [Dishes selected for the five African countries + the US / US Test set (Excel Sheet)](./data/WorldWideDishes_2024_June.xlsx)

## Reproducing experiments

### Setting up the Python environment
```
conda create -n wwd python=3.10
conda activate wwd
pip install -r requirements.txt
```

### Create an `.env` file with settings
Create a `.env` file in the root directory of the repository with the following settings:
```
WWD_CSV_PATH=./data/WorldWideDishes_2024_June_World_Wide_Dishes.csv
WWD_30_DISHES_CSV_PATH=./data/WorldWideDishes_2024_June_Selected_Countries.csv
```
This points to the World Wide Dishes dataset and the 30 dishes selected for the African countries and the US.

### Obtaining an OpenAI API key and Groq API key
If you want to conduct experiments that involve the use of OpenAI products such as GPT 3.5 (required for the [LLM experiments](./llm_probing)), DALL-E 2 and DALL-E 3 (required for the [dish image generation](./gen_images)), 
please [obtain the OpenAI API key from here](https://platform.openai.com/api-keys) and set it as an environment variable `OPENAI_API_KEY` by adding it to the [`.env`](./.env) file. (Make sure you don't commit this file to Git!)

While [Llama 3 (8B) model](https://huggingface.co/meta-llama/Meta-Llama-3-8B) and [Llama 3 (70B) model](https://huggingface.co/meta-llama/Meta-Llama-3-70B) can be run locally by first obtaining a licence through Huggingface from the links provided, 
running these models locally is computationally expensive and time-consuming. 

[Groq](https://groq.com) offers a fast and reliable API service for open-sourced LLMs, including Llama 3 models. As of June 2024, the Groq API is free to use. 
Please [obtain the Groq API key from here](https://console.groq.com/keys) and set it as an environment variable `GROQ_API_KEY` by adding it to the [`.env`](./.env) file.

### LLM Experiments to evaluate common knowledge understanding
Please refer to the README.md in the [`llm_probing`](./llm_probing) directory for instructions on how to run the experiments.
- [LLM Probing source code and README.md](./llm_probing)

### Code for generating images using the World Wide Dishes dataset
Please refer to the README.md in the [`gen_images`](./gen_images) directory for instructions on how to run the experiments.
- [Image Generation source code and README.md](./gen_images)

### CLIP Experiments to evaluate association of generated images with positive and negative descriptors
Please refer to the README.md in the [`clip_probing`](./clip_probing) directory for instructions on how to run the experiments.
- [CLIP Probing source code and README.md](./clip_probing)

### VQA Experiments to probe generated outputs for potential biases
Please refer to the README.md in the [`vqa`](./vqa) directory for instructions on how to run the experiments.
- [VQA source code and README.md](./vqa)

## Community Review of generated images

Due to the high degree of inaccurate and culturally insensitve imagery we will not be releasing the generated images for safety reasons. Our terms of use also prohibits the generation of images for trainign models using the World Wide Dishes dataset.

For transparency and insight into the review conducted, we are releasing the text responses only:

- [Community Reviews](./data/Community_Review_Generated_Dish_Images.csv)
