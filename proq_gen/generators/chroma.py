import os
from langchain_chroma.vectorstores import Chroma
from langchain_huggingface.embeddings import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpointEmbeddings,
)

if os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
    embedding = HuggingFaceEndpointEmbeddings(
        repo_id="sentence-transformers/all-MiniLM-L6-v2",
        huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
    )
else:
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def get_db_store(collection_name="python-questions", persist_directory="./chroma"):
    return Chroma(
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding_function=embedding,
    )
