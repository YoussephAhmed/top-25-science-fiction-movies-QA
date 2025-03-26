# top-25-science-fiction-movies-QA
ask questions about the top 25 science fiction movies using a RAG pipeline 

### Repository Files
- [load_images.py](load_images.py) - Script to extract images and text from the PDF
- [add_images_database.py](add_images_database.py) - Script to add image descriptions to the vector database
- [add_pages_database.py](add_pages_database.py) - Script to add page text to the vector database
- [query.ipynb](query.ipynb) - Jupyter notebook with examples of querying the database

### How to run the code

1. Clone the repository
2. Install the dependencies ```pip install -r requirements.txt```
3. put the openai api key in the .env file
4. run the code ```python load_images.py```
5. run the code ```python add_images_database.py```
6. run the code ```python add_pages_database.py```
7. run the jupyter notebook ```query.ipynb```

### Or you can see some use cases in the [query.ipynb](query.ipynb) directly
