from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_PATH = "chroma"


def main():
    # Initialize the embedding function and Chroma client
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Get all documents from the collection
    results = db.get()

    if not results or not results["documents"]:
        print("No documents found in the database.")
        return

    # Print all documents with their metadata
    print(f"Found {len(results['documents'])} documents:\n")
    for i, (doc, metadata) in enumerate(
        zip(results["documents"], results["metadatas"])
    ):
        print(f"Document {i + 1}:")
        print(f"Content: {doc}")
        print(f"Metadata: {metadata}")
        print("-" * 80 + "\n")


def delete_by_ids(ids):
    """Delete documents from Chroma by their IDs."""
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    try:
        db.delete(ids=ids)
        print(f"Successfully deleted {len(ids)} documents")
    except Exception as e:
        print(f"Error deleting documents: {e}")


if __name__ == "__main__":
    main()
