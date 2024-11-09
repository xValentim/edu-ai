
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_pinecone import PineconeVectorStore
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def format_schemas_output(response_essay: str, 
                          response_schema_essay: Dict, 
                          id_essay: int) -> List[Dict]:
    """Formata a saída dos schemas."""
    schemas_competencias = [x['args'] for x in response_schema_essay.tool_calls]
    raw_feedback_dict = {'raw_feedback': response_essay}
    id_essay_dict = {'id_essay': id_essay}
    
    schemas_competencias.append(id_essay_dict)
    schemas_competencias.append(raw_feedback_dict)
    return schemas_competencias

def vector_db():
    index_name = os.getenv("PINECONE_INDEX_NAME")
    embeddings_size = 3072
    embeddings_model = 'text-embedding-3-large'
    embeddings = OpenAIEmbeddings(model=embeddings_model, dimensions=embeddings_size)
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    return vectorstore

def vector_db_simu():
    MONGODB_ATLAS_CLUSTER_URI = os.getenv('MONGODB_URI')
    client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)
    DB_NAME = os.getenv("DB_NAME")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME")
    embeddings_model = 'text-embedding-3-large'
    ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME")
    MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]
    vectorstore = MongoDBAtlasVectorSearch(
        embedding=OpenAIEmbeddings(model=embeddings_model,
                                   dimensions=1536),
        collection=MONGODB_COLLECTION,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    )
    return vectorstore