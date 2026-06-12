import os
import pandas as pd
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

faqs_path = Path(__file__).parent / "resources/faq_data.csv"
chroma_client = chromadb.Client() # this will process in memory and everything will be lost. if you want permanent data use persistant client
collection_name_faq = 'faqs'
groq_client = Groq()

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='sentence-transformers/all-MiniLM-L6-V2'
)

def ingest_faq_data(path):
    if collection_name_faq not in [c.name for c in chroma_client.list_collections()]:
        print("Ingesting FAQ data into ChromaDB")
        collection = chroma_client.get_or_create_collection(
            name = collection_name_faq,
            embedding_function= ef
        )
        df = pd.read_csv(path)
        docs = df['question'].to_list()
        metadata = [{'answer': ans} for ans in df['answer'].to_list()]
        ids =  [f"id_{i}" for i in range(len(docs))]

        collection.add(
            documents=docs,
            metadatas= metadata,
            ids = ids
        )
    else:
        print(f"===> Collection {collection_name_faq} already exists...!!!")

def get_relavant_qa(query):
    collection = chroma_client.get_collection(name=collection_name_faq)
    result = collection.query(
        query_texts=[query],
        n_results=2
    )
    return result

def faq_chain(query): # go to chroma db and check the matching answers for the query
    result = get_relavant_qa(query)
    context = ''.join([r.get('answer')for r in result['metadatas'][0]]) #add those answers as a string
    answer = generate_answer(query,context)
    print(f"==> : {context}")
    return answer

def generate_answer(query,context):
    prompt = f'''Given the question and context below generate the answer based on the context only.
    If you do not find the answer inside the context then say I Do not know.
    Please do not hallicinate. Consider you as a customer support agent and provide results to customer based on users question

    QUESTION: {query}
    CONTEXT: {context}'''
    #call llm
    completion = groq_client.chat.completions.create(
        model = os.environ['GROQ_MODEL'],
        messages= [
            {
                'role' : 'user',
                'content': prompt
            }
        ]
    )
    #return completion.choices[0].message.content
    return completion.choices[0].message.content

if __name__ == "__main__":
    print(f"====>   {faqs_path}")
    ingest_faq_data(faqs_path)
    query = "Do you acccept cash as payment option?"
    #result = get_relavant_qa(query)
    answer = faq_chain(query)
    print(answer)
