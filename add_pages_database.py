from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import os
import json
import logging

logger = logging.getLogger(__name__)

load_dotenv()
# ---- Set OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

CHROMA_PATH = "chroma"


def process_page_texts(page_texts):
    """Process each page text and save to Chroma database"""
    documents = []

    for page_number, content in page_texts.items():
        # Create a document for each page
        documents.append(
            {
                "file": f"{page_number.replace(' ', '_').lower()}.txt",
                "summary": content,
                "source": f"Page {page_number.split(' ')[1]}",
            }
        )
        print(f"Processed {page_number}")

    # Save all documents to Chroma
    if documents:
        save_to_chroma(documents)
        print(f"Added {len(documents)} pages to the database")


def save_to_chroma(text_documents: list):
    """Save text documents to Chroma database"""
    texts = [doc["summary"] for doc in text_documents]
    metadatas = [
        {"file": doc["file"], "source": doc.get("source", ""), "type": "image"}
        for doc in text_documents
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
        db.add_texts(texts=texts, metadatas=metadatas)
        print(f"Appended {len(texts)} items to {CHROMA_PATH}.")


if __name__ == "__main__":
    # Load the page texts from JSON file
    file_path = "page_texts.json"
    with open(file_path, "r") as file:
        page_texts = json.load(file)

    # Process the page texts and add to database
    process_page_texts(page_texts)
