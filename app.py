#!/usr/bin/env python
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langserve import add_routes
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from services.essay import *
from services.parse import *
from services.mock import *

from models.input_essay import *
from models.schema_query import *
from models.schema_output_search import *
from models.schema_mock import *

from utils import *

load_dotenv()

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

vdb_simu = vector_db_simu()
vdb = vector_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Setting up...")
    
    print("Setup done.")
    yield
    print("Cleaning up...")

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
    lifespan=lifespan,
)

@app.get("/")
def read_root():
    return {"Status": "Running..."}

@app.post("/essay")
async def essay(input_essay: InputEssay):
    path_essay = input_essay.path_essay
    id_essay = input_essay.id_essay
    tema = input_essay.subject
    content_md = await get_parse_md(path_essay)
    chain_essay_md = get_chain_feedback_essay(model="openai")
    chain_essay_schema = get_chain_schema_feedback_essay()
    response_essay = await chain_essay_md.ainvoke({"texto": content_md,
                                            "tema": tema})
    response_schema_essay = await chain_essay_schema.ainvoke({"document": response_essay})
    output = format_schemas_output(response_essay, response_schema_essay, id_essay)
    return output

@app.post("/vector-search-mock")
async def vector_search_mock(input_query: InputQuery):
    
    global vdb_simu
    global vdb
    
    query = input_query.query
    k = min(input_query.k, 10)
    
    retriever_simu = vdb_simu.as_retriever(search_type="similarity", 
                                           search_kwargs={"k": k})
    retriever = vdb.as_retriever(search_type="similarity", 
                                 search_kwargs={"k": k})
    
    response_simu = retriever_simu.invoke(query)
    response_video = retriever.invoke(query)
    
    
    
    output = OutputSearch(response_simu=[x.page_content for x in response_simu], 
                          response_video=[x.page_content for x in response_video])
    
    return output

@app.post("/generate-mock")
async def generate_mock(input_query: InputQuery):

    global vdb_simu
    global vdb
    
    query = input_query.query
    k = min(input_query.k, 10)
    
    retriever_simu = vdb_simu.as_retriever(search_type="similarity", 
                                           search_kwargs={"k": k})
    retriever = vdb.as_retriever(search_type="similarity", 
                                 search_kwargs={"k": k})
    
    chain_final = get_final_chain(model="openai",
                                  retriever_simu=retriever_simu, 
                                  retriever=retriever)
    
    response_structured = chain_final.invoke({"user_query": query})
    
    print(response_structured)
    
    # output = OutputMock(response=response_structured)
    
    return response_structured


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="localhost", port=8000)