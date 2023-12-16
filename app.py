import os
import config
import embeddings_model
import language_model
from langchain.chains import RetrievalQA
import streamlit as st
import boto3

# hugging face textembedding mini lm l6 v2
# meta text generation llama 2 7b

os.environ['AWS_PROFILE'] = config.aws_profile_name
os.environ['AWS_DEFAULT_REGION'] = config.aws_default_region

db = embeddings_model.build()
llm = language_model.build()
PROMPT = language_model.build_prompt()

qa_chain = RetrievalQA.from_chain_type(
    llm,
    chain_type='stuff',
    retriever=db.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

st.title('Ask Anything')
query = st.text_input('Query: ')
if query:
    result = qa_chain({"query": query})
    print(f'Query: {result["query"]}\n')
    print(f'Result: {result["result"]}\n')
    print(f'Context Documents: ')
    for srcdoc in result["source_documents"]:
        print(f'{srcdoc}\n')

    st.write(f'Result: {result["result"]}\n')
    with st.expander('Context Documents'):
        for doc in result["source_documents"]:
            st.info(doc)