# Given an initial file containing the absolute image path and the distance metric between each image and descriptor as measured by cosine similarity, the following code snippet calculates the weighted cosine similarity for each dish in the file. The weighted cosine similarity is calculated as the sum of the cosine similarities for positive descriptors minus the sum of the cosine similarities for negative descriptors. This value is then normalized by the number of dishes and the number of positive descriptors.
# Extract the model name from the file path
# Extract the country name from the file path
# Extract the dish name from the file path
# Merge the df with continent and country data to get the continents for each dish -> can be list of continents
# Get the list of unique continents
# For each model, group the dishes by continent name
# For each continent, extract the list of dish images correspoding to that continent
# Loop through each descriptor group i.e. presentation, taste and style
# For each descriptor group, calculate the  weighted cosine similarity using weights provided by the sentiment analyser or 1 and -1 for each dish in the continent by summing the weighted cosine similarities for each dish and dividing by the number of descriptors
# Calculate the average weighted cosine similarity for each continent by summing the weighted cosine similarities for each dish and dividing by the number of dishes
# Save the output for each continent and model type in a dataframe
# For each descriptor group across all models, normalise the scores by dividing by the maximum possible score
