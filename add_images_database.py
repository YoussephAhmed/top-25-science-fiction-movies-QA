from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import os
import base64
import requests
from io import BytesIO
import logging
import json

logger = logging.getLogger(__name__)

load_dotenv()
# ---- Set OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

CHROMA_PATH = "chroma"

CONTEXT = """
You are an expert in movies and TV show posters.
"""
DATA_PATH = "extracted_images/"

TASK = """
Examine the image carefully and describe the movie or TV show poster from the image and its title and add the rank of the movie in the description.
"""


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def generate_image_summaries(image_titles):
    for image_file, image_title in image_titles.items():
        if image_file.endswith((".png")):
            image_path = os.path.join(DATA_PATH, image_file)
            summary = get_image_summary(image_path, image_title)
            if summary:
                print(f"Generated summary for {image_file} ({image_title}): {summary}")
                # append the file name to the summary
                summary = f"{image_file}: {summary}"
                save_to_chroma(
                    [
                        {
                            "file": image_file,
                            "summary": summary,
                            "source": image_title,
                            "type": "image",
                        }
                    ]
                )


def get_image_summary(image_path, image_title):
    # Encode the image to base64
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": CONTEXT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{TASK}\nThe title of this movie is: {image_title}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        "max_tokens": 15000,
        "temperature": 0.0,
    }

    try:
        # handle errors if any to proceed
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )

        result = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error: {response.status_code}")
        result = None

    return result


def save_to_chroma(image_summaries: list):
    texts = [summary["summary"] for summary in image_summaries]
    metadatas = [
        {
            "file": summary["file"],
            "source": summary.get("source", ""),
            "type": summary.get("type", ""),
        }
        for summary in image_summaries
    ]
    embeddings = OpenAIEmbeddings()

    if not os.path.exists(CHROMA_PATH):
        db = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            persist_directory=CHROMA_PATH,
        )
        print(f"Created new database with {len(texts)} items in {CHROMA_PATH}.")
    else:
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        db.add_texts(texts=texts, metadatas=metadatas, embeddings=embeddings)
        print(f"Appended {len(texts)} items to {CHROMA_PATH}.")


if __name__ == "__main__":
    file_path = "image_titles.json"
    with open(file_path, "r") as file:
        image_titles = json.load(file)

    generate_image_summaries(image_titles)
