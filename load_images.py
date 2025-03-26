import fitz  # PyMuPDF
from PIL import Image
import io
import os
import re
import json


def extract_images_from_pdf(pdf_path, output_folder, min_dimension):
    """
    Extracts images from a PDF and saves them to the specified folder.

    :param pdf_path: Path to the input PDF file.
    :param output_folder: Folder to save extracted images.
    :param min_dimension: Minimum dimension (width or height) in pixels to save an image.
    """
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Counters for tracking
    total_images = 0
    saved_images = 0

    # Initialize counter for image filenames
    image_index = 0

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        if page_num == 0:
            continue
        image_list = page.get_images(full=True)

        # Extract images from the page
        for img_index, img in enumerate(image_list, start=1):
            total_images += 1
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Check image dimensions using PIL
            img_obj = Image.open(io.BytesIO(image_bytes))
            width, height = img_obj.size

            # Skip images smaller than the minimum dimension
            if width <= min_dimension or height <= min_dimension:
                continue

            # Save the image
            saved_images += 1
            image_index = 26 - saved_images
            image_filename = f"{image_index}.{image_ext}"
            image_path = os.path.join(output_folder, image_filename)
            img_obj.save(image_path)
            image_index += 1

    doc.close()
    print(f"Images extracted to folder: {output_folder}")
    print(f"Total images found: {total_images}")
    print(f"Images saved (dimensions >= {min_dimension}px): {saved_images}")
    print(
        f"Images skipped (dimensions < {min_dimension}px): {total_images - saved_images}"
    )


def extract_information_from_pdf(extracted_folder, pdf_path):
    """
    Extracts information from the PDF (e.g., movie titles, full text).

    :param extracted_folder: Path to the folder containing extracted images
    :param pdf_path: Path to the PDF file to search for movie titles
    :return: Dictionary mapping image filenames to their matching movie titles, and dictionary of page text
    """
    # Get list of image files in the extracted folder
    image_files = [
        f
        for f in os.listdir(extracted_folder)
        if os.path.isfile(os.path.join(extracted_folder, f))
    ]

    # Sort image files by their numeric base name
    image_files.sort(
        key=lambda f: (
            int(os.path.splitext(f)[0])
            if os.path.splitext(f)[0].isdigit()
            else float("inf")
        )
    )

    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Dictionary to store image filename to title mappings
    image_to_title = {}

    # Dictionary to store page number to text mappings
    page_text = {}

    # List to collect all movie titles
    movie_titles = []

    # Modified regex pattern for movie titles - allowing multi-line titles
    title_pattern = r"(?:^|\n|\. )(\d{1,2})\.\s+(.*?)\s*\((\d{4})\)"

    # Iterate through each page to extract text and find movie titles
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        # Store page text in the dictionary
        page_text[f"page {page_num + 1}"] = text

        # Find all movie title matches in the text
        matches = re.finditer(title_pattern, text, re.DOTALL)
        for match in matches:
            number = match.group(1)
            title = match.group(2).strip()
            year = match.group(3)
            formatted_title = f"{number}. {title} ({year})"
            movie_titles.append(formatted_title)

    for i, img_file in enumerate(reversed(image_files)):
        if i < len(movie_titles):
            image_to_title[img_file] = movie_titles[i]

    doc.close()
    return image_to_title, page_text


if __name__ == "__main__":
    pdf_filename = "The-25-Best-Sci-Fi-Movies-of-All-Time-IGN-1-37.pdf"
    extracted_folder = "extracted_images"
    extract_images_from_pdf(
        pdf_path=pdf_filename, output_folder=extracted_folder, min_dimension=600
    )
    image_titles, page_texts = extract_information_from_pdf(
        extracted_folder, pdf_filename
    )

    # Save dictionaries to JSON files
    with open("image_titles.json", "w") as f:
        json.dump(image_titles, f, indent=4)

    with open("page_texts.json", "w") as f:
        json.dump(page_texts, f, indent=4)
