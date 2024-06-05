## LLM Experiments to evaluate common knowledge 

Code to make predictions using an LLM about the properties of a dish given its dish name and country of origin is available in this directory.
We used GPT 3.5, Llama 3 (8B) and Llama 3 (70B) models to make predictions about the properties of the dishes.

In the following instructions, we assume that you are running your code from the root directory of the repository (`world-wide-dishes`).

### The LLM prompts
The aim is to evaluate the common knowledge understanding of the LLMs about dishes from around the globe.

The dish properties of interest are the ones that we curated feedback for in the World Wide Dishes dataset,  
include the country of origin, region, associated culture, time of day when the meal is typically eaten, 
type of meal, utensils used, typically accompanied drink, ingredients, and the occasion at which the dish is eaten.

Out of these properties, we focus on the time of day, the type of meal, utensils, and ingredients to compute quantitative metrics.
The metric of choice is the IoU (Intersection over Union) score, which is a measure of the overlap between the predicted and the ground truth set of properties.
[Here are the prompts used.](./prompts/llm_probing.yaml)

### Obtaining an OpenAI API key and Groq API key
If you want to conduct experiments that involve the use of OpenAI products such as GPT 3.5 (required for the [LLM experiments](./llm_probing)), DALL-E 2 and DALL-E 3 (required for the [dish image generation](./gen_images)), 
please [obtain the OpenAI API key from here](https://platform.openai.com/api-keys) and set it as an environment variable `OPENAI_API_KEY` by adding it to the [`.env`](./.env) file. (Make sure you don't commit this file to Git!)

While [Llama 3 (8B) model](https://huggingface.co/meta-llama/Meta-Llama-3-8B) and [Llama 3 (70B) model](https://huggingface.co/meta-llama/Meta-Llama-3-70B) can be run locally by first obtaining a licence through Huggingface from the links provided, 
running these models locally is computationally expensive and time-consuming. 

[Groq](https://groq.com) offers a fast and reliable API service for open-sourced LLMs, including Llama 3 models. As of June 2024, the Groq API is free to use. 
Please [obtain the Groq API key from here](https://console.groq.com/keys) and set it as an environment variable `GROQ_API_KEY` by adding it to the [`.env`](./.env) file.

### Querying the LLMs
To query the LLMs for the properties of the dishes, run the following:
```bash
python ./llm_probing/probe_llm.py --model gpt35 -n 5 --save-root ./outputs
```
- The `model` option can be set to `gpt35`, `llama3-8B` or `llama3-70B`.
- The `n` option specifies the number of predictions to make per dish.
- The `save-root` option specifies the directory to save the predictions to.

### Cleaning up the LLM outputs
The LLM fails to generate outputs for some dishes. 
To identify the failure modes, we perform keyword checks using the following script:
```bash
python ./llm_probing/llm_failures.py <path-to-csv>
````
This will generate a CSV file with the failure modes with a `_failures.csv` suffix.

### Cleaning up the LLM outputs
The LLM outputs saved in the `outputs` directory still contains outputs that do not strictly adhere to the [schema](./prompts/autoclean_schema.json) of the output.
We clean up the output format by making the LLM check the outputs and compare them against the schema. 
```bash
python ./llm_probing/llm_cleanup_df.py <path-to-csv>
```
This will generate a CSV file with the failure modes with a `_cleaned.csv` suffix.

### Compare against the World Wide Dishes dataset
To compare the LLM outputs against the World Wide Dishes dataset, run the following:
```bash
python ./llm_probing/compare_llm_to_wwd.py <path-to-cleaned-csv>
```
This will generate a CSV file with the failure modes with a `_compared.csv` suffix.

### Compute statistics for the results
To compute the IoU scores and failure frequencies for the LLM outputs, run the following:
```bash
python ./llm_probing/llm_stats.py <path-to-cleaned-csv>
```
This will generate a CSV file containing the relevant entries with a `_results.csv` suffix, and another CSV file containing the statistics with a `_stats.csv` suffix.
