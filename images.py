import os
import requests

# API URL
api_url = "https://api.prov.vic.gov.au/search/query?wt=json&q=(series_id%3A(12800))%20AND%20((record_form%3A%22Photograph%20or%20Image%22))%20AND%20(iiif-manifest%3A(*))"

# Desired image dimensions
image_width = 500
image_height = 500

# Make a GET request to the API
response = requests.get(api_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    json_data = response.json()

    # Extract the list of items (images) from the JSON data
    image_items = json_data.get("response", {}).get("docs", [])
    print(image_items)

    # Directory to save the downloaded images
    save_directory = "images"

    # Create the save directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)

    # Loop through each image item and download the image
    for item in image_items:
        # Access the URL and filename within the item
        image_url = item.get("iiif-thumbnail")
        image_filename = os.path.join(save_directory, f"{item['_id']}.jpg")

        print(f"Downloading image from: {image_url}")  # Print the image URL

        # Download the image and save it to the specified directory
        image_response = requests.get(image_url, verify=True)
        if image_response.status_code == 200:
            with open(image_filename, "wb") as image_file:
                image_file.write(image_response.content)
                print(f"Downloaded: {image_filename}")
        else:
            print(f"Failed to download: {image_url}")
else:
    print("API request failed.")
