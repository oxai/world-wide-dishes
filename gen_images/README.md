## Code for generating images using the World Wide Dishes dataset

Code to generate dish images using DALL-E 2, DALL-E 3 and Stable Diffusion is available in this directory.
Stable Diffusion is an open-sourced image generation model that can be run locally. DALL-E 2 and DALL-E 3 require an API key to run.

In the following instructions, we assume that you are running your code from the root directory of the repository (`world-wide-dishes`).

### Obtaining an OpenAI API key
If you want to conduct experiments that involve the use of OpenAI products such as GPT 3.5 (required for the [LLM experiments](./llm_probing)), DALL-E 2 and DALL-E 3 (required for the [dish image generation](./gen_images)), 
please [obtain the OpenAI API key from here](https://platform.openai.com/api-keys) and set it as an environment variable `OPENAI_API_KEY` by adding it to the [`.env`](./.env) file. (Make sure you don't commit this file to Git!)

### Generate images of dishes submitted to World Wide Dishes
We use the prompt: 
```
f"Generate a photograph of food from {countries} called {local_name}. The food should be served, ready to be eaten."
```

To generate these images, run the following:
```bash
python ./gen_images/iterate_dishes.py --model all --n_images 5 --save-root ./outputs
```

- The `model` option can be set to `dalle2`, `dalle3`, `sd21` or `all`. 
- The `n_images` option specifies the number of images to generate per dish. 
- The `save-root` option specifies the directory to save the images to.

### Generate images of dishes from all countries and notable regions

To generate images of dishes from all countries, run the following:
```bash
python ./gen_images/iterate_countries.py --model all
```

### Generate images for the world, continents, and selected countries for case study
Continents: "Africa", "Asia", "Europe", "North America", "South America", "Oceania"
Selected countries: "Nigeria", "Cameroon", "Algeria", "South Africa", "Kenya", "the United States of America"

```bash
python ./gen_images/iterate_selected_places.py --model all
```

### Generate images of selected dishes for the chosen case study countries
Selected countries: "Nigeria", "Cameroon", "Algeria", "South Africa", "Kenya", "the United States of America"
Selected dishes: [Dishes selected for the five African countries + the US](./data/WorldWideDishes_2024_June_Selected_Countries.csv)

```bash
python ./gen_images/iterate_selected_dishes.py --model all
```

### Generate custom dishes
To generate images of custom dishes from a given country, run the following:
```bash
python ./gen_images/generate_dishes.py --model all --dish-list "Country 1" "Dish name 1" "Country 2" "Dish name 2" ...
```
