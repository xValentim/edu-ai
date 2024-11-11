# from utils import*

import base64
import mimetypes

from io import StringIO
from openai import OpenAI
from PyPDF2 import PdfReader

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain_groq import ChatGroq
from models.schema_grade import *

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from pydantic import BaseModel, Field
from typing import List

load_dotenv()

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def format_questoes(questoes):
    return "\n\n".join([tema for tema in questoes])

def format_output_mock(response_schema):
    try:
        args = response_schema.tool_calls[0]['args']
    except:
        return {
            "question": 'EMPTY',
            "options": ['EMPTY'] * 5,
            "answer": 'EMPTY'
        }

    new_output = []
    for q, o, a in zip(args['questions'], args['options'], args['answers']):
        element = {
            "question": q,
            "options": o.split('\n'),
            "answer": a
        }
        new_output.append(element)
    return new_output

def get_chain_format_schema():
    
    system_prompt = """
    Você é um bot chamado Edu e foi desenvolvido pela Nero.AI. Você vai pegar o simulado gerado e criar questões para compor um simulado do ENEM.
    """

    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt), 
                ("human", "Simulado: \n\n {mock}")
            ]
    )

    model_name = "gpt-4o-2024-08-06"

    llm = ChatOpenAI(
        model="gpt-4o-2024-08-06", # 100% json output
        temperature=0,
    )

    class GetMockSchema(BaseModel):
        """Extrai schema de simulados -> questões e gabarito"""

        questions: List[str] = Field(description="As 5 principais questões do simulado")
        options: List[str] = Field(description="As 5 alternativas de cada questão")
        answers: List[str] = Field(description="As respostas corretas de cada questão")

    llm_with_tools_extraction = llm.bind_tools([GetMockSchema]) #, strict=True)
    chain_structured_extraction = prompt | llm_with_tools_extraction | RunnableLambda(format_output_mock)
    
    return chain_structured_extraction

def get_chain_mock(retriever_simu, 
                   retriever, 
                   model="openai"):
    
    if model == "openai":
        _chat_ = ChatOpenAI
        _model_name_ = "gpt-4o-2024-08-06"
    elif model == "groq":
        _chat_ = ChatGroq
        _model_name_ = "llama-3.2-90b-text-preview"
    
    template = """
    Você é um assistente de modelo de linguagem de IA que irá gerar simulados. Sua tarefa é separar cada uma das matérias ou temas
    que o usuário deseja estudar e gerar uma curta query descrevendo o temas, para facilitar a busca por similaridade.
    A entrada do usuário pode ter uma ou mais matérias ou temas.
    Forneça esses temas/matérias separados por novas linhas, no formato:
    - Tema1: Descricao do tema1
    - Tema2: Descricao do tema2
    e assim por diante.
    Separe os temas em: {user_query}"""
    
    template_1 = [
        ('system', """
                    Você é um bot chamado Edu e foi desenvolvido pela Nero.AI. 
                    Você irá gerar questões para compor um simulado do ENEM."""),
        ('system', "Use essas questões como exemplo de estrutura de questão\n\n{context_query_simu}\n\n"),
        ('system', "Use esses documentos para embasar o conteúdo das questões\n\n{context_query_video}\n\n"),
        ('system', "Não crie questões unicamente objetivas, como 'O que é?', 'Quem foi?', contextualize breventemente o tema e crie questões que exijam raciocínio."),
        ('system', """Forneça essas perguntas alternativas separadas por novas linhas. \n:
            Siga a estrutura usando markdown:
            Tema: (tema_questao)\n
         
            QUESTÃO 1: (questao_1)\n
            a) alternativa 1
            b) alternativa 2
            c) alternativa 3
            d) alternativa 4
            e) alternativa 5

            QUESTÃO 2: (questao_2)
            a) alternativa 1
            b) alternativa 2
            c) alternativa 3
            d) alternativa 4
            e) alternativa 5

        e assim por diante.
            Gabarito: 1 - (letra correspondente a alternativa)\n
                      2 - (letra correspondente a alternativa)\n
        e assim por diante.
        """),
        ('system', "Gere apenas 5 questões sobre o tema: {tema_questao}"),
    ]
    
    prompt1 = ChatPromptTemplate.from_messages(template_1)
    
    prompt = ChatPromptTemplate.from_template(template)

    llm = _chat_(temperature=0.1, model=_model_name_)

    generate_temas = (
        prompt
        | llm
        | StrOutputParser()
        | (lambda x: x.split("\n"))
    )

    chain_rag_simu = retriever_simu | format_docs
    chain_rag_video = retriever | format_docs

    chain_rag = (
        {
            "context_query_simu": RunnablePassthrough() | chain_rag_simu,
            "context_query_video": RunnablePassthrough() | chain_rag_video,
            "tema_questao": RunnablePassthrough()
        }
        | prompt1
        | llm
        | StrOutputParser()
    )
    
    chain = generate_temas | chain_rag.map() | format_questoes | StrOutputParser()
    
    return chain

def get_final_chain(retriever_simu, retriever, model="openai", ):
    chain_mock = get_chain_mock(model=model,
                                retriever_simu=retriever_simu, 
                                retriever=retriever)
    chain_schema_mock = get_chain_format_schema()
    
    chain_final = chain_mock | chain_schema_mock
    return chain_final