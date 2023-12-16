from typing import Dict
from langchain import PromptTemplate, SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import RetrievalQA
import streamlit as st
import json
import boto3
import os
import config

llm_model_endpoint_name = config.aws_sagemaker_llm_model_endpoint
os.environ['AWS_PROFILE'] = config.aws_profile_name
os.environ['AWS_DEFAULT_REGION'] = config.aws_default_region

class QAContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"
    
    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps(
            {"inputs": [
                [
                    {
                        "role": "system",
                        "content": ""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]],
                "parameters": {**model_kwargs}
            })
        return input_str.encode('utf-8')
    
    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generation"]["content"]

@st.cache_resource
def build_prompt():
    print("Building prompt template for use with LLM")

    prompt_template = """
    <s>[INST] <<SYS>>
    Use the context provided to answer the question at the end. If you don't know the answer just say that you don't know, don't try to make up an answer.
    <</SYS>>

    Context:
    --------------
    {context}
    --------------

    Question: {question} [/INST]
    """

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    return PROMPT

@st.cache_resource
def build():
    print("Building LLM")

    qa_content_handler = QAContentHandler()
    llm = SagemakerEndpoint(
        endpoint_name=llm_model_endpoint_name,
        region_name=boto3.Session().region_name,
        model_kwargs={"max_new_tokens": 1000, "top_p": 0.9, "temperature": 1e-11},
        endpoint_kwargs={"CustomAttributes": 'accept_eula=true'},
        content_handler=qa_content_handler
    )

    print("Language model build completed.")

    return llm

def test_llm(llm, query):
    print("Test LLM functionality with a simple query.")
    llm.predict(query)
    

