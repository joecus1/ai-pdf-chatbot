from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain.schema import Document
from langchain.vectorstores import FAISS
import boto3
import pullpdfs
import os
import json
from sagemaker.jumpstart.model import JumpStartModel
from typing import Dict, List
import config
import streamlit as st

embedding_model_endpoint_name = config.aws_sagemaker_embeddings_model_endpoint

class CustomEmbeddingsContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"
    
    def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"text_inputs": inputs, **model_kwargs})
        return input_str.encode("utf-8")
    
    def transform_output(self, output: bytes) -> List[List[float]]:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["embedding"]

@st.cache_data
def makeChunks(filenames, metadata, data_root):
    print("Splitting retrieved documents into chunks.")
    documents = []
    for idx, file in enumerate(filenames):
        loader = PyPDFLoader(data_root + file)
        document = loader.load()
        for document_fragment in document:
            document_fragment.metadata = metadata[idx]
            
        documents += document
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 512,
        chunk_overlap = 100,
    )

    docs = text_splitter.split_documents(documents)

    print("\nDocumens split into chunks.")
    print(f'# of document pages {len(documents)}')
    print(f'# of document chunks: {len(docs)}')

    return docs

@st.cache_resource
def build():
    print("Building embedding model.")
    filenames, metadata, data_root = pullpdfs.pull()
    docs = makeChunks(filenames, metadata, data_root)

    embeddings_content_handler = CustomEmbeddingsContentHandler()

    embeddings = SagemakerEndpointEmbeddings(
        endpoint_name=embedding_model_endpoint_name,
        region_name=boto3.Session().region_name,
        content_handler=embeddings_content_handler
    )

    db = FAISS.from_documents(docs, embeddings)
    print("Embedding model completed and vector DB completed")

    return db

def test_db(db):
    print("Testing vector DB functionality.")
    query = "Why is Amazon successful?"
    results_with_scores = db.similarity_search_with_score(query)

    for doc, score in results_with_scores:
        print(f"Content: {doc.page_content}\nMetadata: {doc.metadata}\nScore: {score}\n\n")


