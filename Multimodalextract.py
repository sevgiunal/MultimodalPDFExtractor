import json
import base64
import pymupdf
import requests
import os
from tqdm import tqdm
from collections import defaultdict
import json


url = "https://downloads.bbc.co.uk/skillswise/maths/ma37grap/quiz/ma37grap-l1-quiz.pdf"

filename = "BBCPaper.pdf"
filepath = os.path.join("data", filename)

os.makedirs("data", exist_ok=True)

# Download the file
response = requests.get(url)
with open(filepath, 'wb') as file:
    file.write(response.content)
print(f"File downloaded successfully: {filepath}")


# Process text 
def process_text_chunks(text, page_num, base_dir, items):
    text_file_name = f"{base_dir}/text/{os.path.basename(filepath)}_text_{page_num}_0.txt"
    with open(text_file_name, 'w') as f:
        f.write(text)
    items.append({"page": page_num, "type": "text", "text": text, "path": text_file_name})

# Process images
def process_images(page, page_num, base_dir, items):
    images = page.get_images()
    for idx, image in enumerate(images):
        xref = image[0]
        pix = pymupdf.Pixmap(doc, xref)
        image_name = f"{base_dir}/images/{os.path.basename(filepath)}_image_{page_num}_{idx}_{xref}.png"
        pix.save(image_name)
        with open(image_name, 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('utf8')
        items.append({"page": page_num, "type": "image", "path": image_name, "image": encoded_image})

doc = pymupdf.open(filepath)
num_pages = len(doc)
base_dir = "data"

# Creating the directories
os.makedirs(os.path.join("data", "images"), exist_ok=True)
os.makedirs(os.path.join("data", "text"), exist_ok=True)

    
items = []

#Process each page of the PDF
for page_num in tqdm(range(num_pages), desc="Processing PDF pages"):
    page = doc[page_num]
    text = page.get_text()

    process_text_chunks(text, page_num, base_dir, items)

    process_images(page, page_num, base_dir, items)


# Group items by page
pages = defaultdict(lambda: {"text_chunks": [], "tables": [], "images": [], "page_image": None})

for item in items:
    page_num = item["page"]
    if item["type"] == "text":
        pages[page_num]["text_chunks"].append({
            "path": item["path"],
            "content": item["text"]
        })
    elif item["type"] == "image":
        pages[page_num]["images"].append({
            "path": item["path"],
        })

# Convert to list of pages sorted by page number
final_json = [{"page": page, **content} for page, content in sorted(pages.items())]

# Save the JSON to disk 
with open("processed_output.json", "w") as f:
    json.dump(final_json, f, indent=2)

print("Final JSON saved as processed_output.json")
