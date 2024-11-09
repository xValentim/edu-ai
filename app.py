#!/usr/bin/env python
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langserve import add_routes
from dotenv import load_dotenv

from services.essay import *
from services.parse import *
from models.input_essay import *
from utils import *

load_dotenv()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

@app.get("/")
def read_root():
    return {"Status": "Running..."}

@app.post("/essay")
async def essay(input_essay: InputEssay):
    path_essay = input_essay.path_essay
    id_essay = input_essay.id_essay
    tema = input_essay.subject
    content_md = get_parse_md(path_essay)
    chain_essay_md = get_chain_feedback_essay(model="groq")
    chain_essay_schema = get_chain_schema_feedback_essay()
    response_essay = chain_essay_md.invoke({"texto": content_md,
                                            "tema": tema})
    response_schema_essay = chain_essay_schema.invoke({"document": response_essay})
    output = format_schemas_output(response_essay, response_schema_essay, id_essay)
    return output


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="localhost", port=8000)