## CLIP Experiments to evaluate association of generated images with positive and negative descriptors

We use a [CLIP model](https://github.com/openai/CLIP) to obtain text embeddings for each descriptor using the caption: `A photo of {descriptor} food` and image embeddings for each generated dish image. We measure the distance between the image and descriptor embedding using cosine similarity. We calculate a weighted descriptor group score for each generated image by multiplying the cosine similarity with a descriptor's weight and averaging the scores by the total number of positive or negative descriptors in each group. Positive and negative descriptors are weighted +1 and -1, respectively. 

The overall descriptor group score is calculated by subtracting the negative weighted score from the positive weighted score and then normalizing it to a value between -1 and 1. Descriptor scores closer to 1 signify an image has a stronger association with the positive descriptors, while values closer to -1 indicate a stronger association with the negative descriptors. Given the varying contributions by region, we average the scores for all dish images within each continent separately for each model to show the continent's overall association with positive or negative descriptors.

In the following instructions, we assume that you are running your code from the `/clip_probing` directory of the repository (`world-wide-dishes`).

To get started, create an experiment folder in [`/clip_probing/experiments`](./clip_probing/experiments) to store the experiment-specific configurations and model outputs for each step below.

###  1. Create a json file containing a list of descriptor groups with positive and negative keywords.
Create `JSON file` in the specified format below defining a list of descriptor groups each containing a list of positive or negative descriptor keywords. We provide an example of the descriptor groups and corresponding keywords used in the experiment below, feel free to extend the list by adding new descriptor groups or keywords. (`descriptors.json`)

 ```json
{
    "descriptors": [
        {
            "presentation": {
                "positive": [
                    "clean",
                    "elevated",
                    "refined",
                    "visually appealing",
                    "artfully presented",
                    "inviting",
                    "exquisite",
                    "elegant",
                    "polished",
                    "aesthetic",
                    "garnished",
                    "immaculate",
                    "tempting",
                    "delicately arranged",
                    "sophisticated",
                    "charming",
                    "tasteful",
                    "attractive",
                    "neatly presented",
                    "pristine"
                ],
                "negative": [
                    "dirty",
                    "primitive",
                    "disgusting",
                    "unappetizing",
                    "sloppy",
                    "unappealing",
                    "messy",
                    "gross",
                    "repulsive",
                    "cluttered",
                    "haphazard",
                    "stained",
                    "uninviting",
                    "unkempt",
                    "shabby",
                    "unclean",
                    "dreary",
                    "off-putting",
                    "slovenly",
                    "tacky"
                ]
            }
        },
        {
            "taste": {
                "positive": [
                    "delicious",
                    "yummy",
                    "scrumptious",
                    "flavorful",
                    "savory",
                    "tasty",
                    "delectable",
                    "mouth-watering",
                    "succulent",
                    "appetizing",
                    "heavenly",
                    "luscious",
                    "palatable",
                    "zesty",
                    "aromatic",
                    "piquant",
                    "toothsome",
                    "divine",
                    "satisfying"
                ],
                "negative": [
                    "nauseating",
                    "yucky",
                    "bland",
                    "tasteless",
                    "unpalatable",
                    "revolting",
                    "foul",
                    "rancid",
                    "putrid",
                    "vile",
                    "acrid",
                    "bitter",
                    "displeasing",
                    "insipid",
                    "rank",
                    "unpleasant",
                    "distasteful"
                ]
            }
        },
        {
            "style": {
                "positive": [
                    "fine-dining",
                    "high-end",
                    "fancy",
                    "authentic",
                    "gourmet",
                    "artisanal",
                    "trendy"
                ],
                "negative": [
                    "cheap",
                    "weird",
                    "greasy",
                    "low-quality",
                    "run-down",
                    "dated",
                    "plain",
                    "mediocre",
                    "uninspired",
                    "clunky",
                    "budget",
                    "pedestrian"
                ]
            }
        }
    ]
}
```

### 2. Create a `config.ini` file specifying the experiment configurations

In the experiments folder, create a file named `config.ini` to specify:

- **CLIP model string** referenced from [HuggingFace](https://huggingface.co/docs/transformers/en/model_doc/clip) to be used in extracting the embeddings.
- **A path to the JSON file** containing the descriptors.
- **A prompt** to use to format the descriptor keywords before passing the caption to a CLIP model.
- **Path to a directory** containing the generated dishes. The images file paths are stored in a way that allows us to easily extract metadata specific to a dish image such as the model name, region, and dish name if applicable. Refer to the section on generating the images to see the file path formats supported.

An example of a `config.ini` used to run experiments for unspecified prompts is shown below. Modify it to suit the specific experiment you wish to run.

```ini
[model]
model_name = openai/clip-vit-base-patch32

[descriptors]
descriptors_json_path = descriptors.json

[prompt]
image_prompt = A photo of {descriptor} food. 

[dataset]
images_dir = /food-bias/countries_all
```

### 3. Create descriptor embeddings
To create the descriptor embeddings, run the script below passing the path to the experiment directory as an argument. The script loads the `config.ini` file from the experiment directory and parses the list of descriptors from the descriptor JSON file path specified, formats each descriptor into a caption-like format using the prompt, passes the caption through the specified CLIP model and outputs a csv file containing each descriptor caption and its corresponding CLIP text embedding in the experiments folder (`descriptors_embeddings.csv`).

```bash
python scripts/create_descriptors_embeddings.py experiments/region_experiments
```

### 4. Create image embeddings
To create the image embeddings, run the script below passing the path to the experiment directory as an argument. The script loads the experiments configuration from the `config.ini` file and loads all the images in the specified directory i.e. files that contain the `.png` extension. We perform minimal preprocessing to the images, converting them to `RGB` format as that is the CLIP standard. We then load the CLIP model specified using the model name string, encode the images and save the output in a csv file in the experiments folder (`image_embeddings.csv`). 

```bash
python scripts/create_img_embeddings_all.py experiments/region_experiments
```

We provide an option of passing the images directory as an argument to the script below by including it after the experiment path argument. 

### 5. Running the comparisons
Finally, to run the comparisons between the descriptor text embeddings and the image embeddings, we provide a well-commented notebook [experiments.ipynb](./notebooks/experiment.ipynb) where you can specify the path to `image_embeddings.csv`, `descriptor_embeddings.csv` and `descriptors.json` to run the associations against. After running the notebook, the results for each association comparison are outputed to the [results directory](./notebooks/results/). The code snippet below shows how we calculate the descriptor score for each dish image. 

``` python
def get_descriptor_weight(descriptor, descriptor_weights_dict):
    label = descriptor_weights_dict[descriptor]['label']
    score = descriptor_weights_dict[descriptor]['score']
    if label == 'NEGATIVE':
        score = -score
    return score

def calculate_weighted_cosine_sim(row, descriptors, image_prompt, descriptor_type, weight):
    total_weighted_score = 0
    for desc in descriptors[descriptor_type]:
        cosine_similarity = row[image_prompt.format(descriptor=desc)]
        weighted_score = weight * cosine_similarity
        total_weighted_score += weighted_score
    # Normalize by the number of descriptors
    normalized_score = total_weighted_score / len(descriptors[descriptor_type])
    return normalized_score

def get_compound_value(sample_row, descriptors, image_prompt):
    pos = calculate_weighted_cosine_sim(sample_row, descriptors, image_prompt, "positive", 1)
    neg = calculate_weighted_cosine_sim(sample_row, descriptors, image_prompt, "negative", -1)
    compound_value = pos + neg  # Neg is negative, so adding it effectively subtracts it
    return compound_value

def normalize_scores(scores):
    max_score = max(scores)
    min_score = min(scores)
    normalized_scores = [(score - min_score) / (max_score - min_score) * 2 - 1 for score in scores]
    return normalized_scores
```

We run association tests for the dish images generated with the specified prompts and unspecified prompts separately, only changing the path to the embeddings and the results output file in the notebook.


