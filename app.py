import os
import requests
from flask import Flask, render_template, request, send_file, redirect, url_for

app = Flask(__name__)

# API URL
api_url = "https://api.prov.vic.gov.au/search/query?wt=json&q=(series_id%3A(12800))%20AND%20((record_form%3A%22Photograph%20or%20Image%22))%20AND%20(iiif-manifest%3A(*))"

# Original image dimensions in the URL
original_dimensions = "200,200"

# Desired image dimensions
image_width = 400
image_height = 400

# Directory to save the downloaded images
image_directory = "images"
os.makedirs(image_directory, exist_ok=True)

# Route to display the list of images
@app.route("/", methods=["GET"])
def index():
    api_url = "https://api.prov.vic.gov.au/search/query?wt=json&q=(series_id%3A(12800))%20AND%20((record_form%3A%22Photograph%20or%20Image%22))%20AND%20(iiif-manifest%3A(*))"
    
    response = requests.get(api_url)
    if response.status_code == 200:
        json_data = response.json()
        image_items = json_data.get("response", {}).get("docs", [])
        
        # Extract available series IDs from the response
        available_series_ids = list(set(item.get("series_id", "N/A") for item in image_items))
        
        selected_series = request.args.get("series_id", "")  # Default to no filter
        
        if selected_series:
            filtered_items = [item for item in image_items if item.get("series_id") == selected_series]
        else:
            filtered_items = image_items
        
        download_successful = request.args.get("download_successful")
        return render_template(
            "index.html",
            image_items=filtered_items,
            available_series_ids=available_series_ids,
            selected_series=selected_series,
            download_successful=download_successful
        )
    else:
        return "API request failed."


# Route to download selected images
@app.route("/download", methods=["POST"])
def download_images():
    selected_image_ids = request.form.getlist("selected_images")

    response = requests.get(api_url)
    if response.status_code == 200:
        json_data = response.json()
        image_items = json_data.get("response", {}).get("docs", [])
    else:
        return "API request failed."

    for image_id in selected_image_ids:
        # Find the corresponding image item by ID
        for item in image_items:
            if item['_id'] == image_id:
                image_url = item.get("iiif-thumbnail")
                image_filename = os.path.join(image_directory, f"{image_id}_{image_width}x{image_height}.jpg")
                modified_url = image_url.replace(original_dimensions, f"{image_width},{image_height}")
                image_response = requests.get(modified_url, verify=True)
                if image_response.status_code == 200:
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_response.content)
                else:
                    return f"Failed to download image: {image_url}"

    return redirect(url_for("index", download_successful=True))

if __name__ == "__main__":
    app.run(debug=True)
