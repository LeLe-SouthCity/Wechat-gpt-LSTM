import faiss,os,re
from typing import List, Dict, Callable, Optional, Tuple
import json
import redis
import openai
import ast
import getpass
from langchain_community.vectorstores.redis import Redis
from langchain.agents import load_tools
import logging
import tiktoken
from io import BytesIO
from streamlit import file_uploader, write, info
import fitz  # PyMuPDF
from pathlib import Path
from langchain.schema import (
    BaseChatMessageHistory
)
from langchain.utilities.redis import get_client
import jieba
from abc import ABC, abstractmethod
from langchain.schema.messages import AIMessage, BaseMessage, HumanMessage
from pyparsing import Literal
from langchain.vectorstores.chroma import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.memory.chat_memory import ChatMessageHistory
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.embeddings import MiniMaxEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema.language_model import BaseLanguageModel
from pydantic import BaseModel, Field, validator
from langchain.llms.openai import OpenAI,OpenAIChat
from langchain.llms.minimax import Minimax
from langchain.agents.react.base import DocstoreExplorer, Tool
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_community.utilities import GoogleSearchAPIWrapper,SerpAPIWrapper
from langchain.memory import VectorStoreRetrieverMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.callbacks import get_openai_callback
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import ChatGLM
from langchain.schema import (
    HumanMessage,
    SystemMessage,
)
# import os
from langchain.memory import ConversationBufferMemory,ConversationBufferWindowMemory,ReadOnlySharedMemory
# FakeEmbeddings 不用花钱
from langchain.schema import (
    AgentAction, AgentFinish, HumanMessage,BaseRetriever, Document
)
from langchain.embeddings.fake import DeterministicFakeEmbedding, FakeEmbeddings
from langchain.chains import (
    StuffDocumentsChain, LLMChain, ConversationalRetrievalChain,RetrievalQA,
    ConversationalRetrievalChain,StuffDocumentsChain, LLMChain,
    RetrievalQAWithSourcesChain
)
from langchain.agents import (
    ZeroShotAgent, Tool, AgentExecutor,initialize_agent,AgentType
)
from langchain.prompts import (
    PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate,
    BaseChatPromptTemplate,StringPromptTemplate
)
from langchain_community.document_loaders import (
    PyPDFLoader,TextLoader,UnstructuredFileLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter,CharacterTextSplitter
from typing import (
    Any, Dict, List, Optional, Sequence, Tuple, Union
)
from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo,
)
from langchain.output_parsers import (
    CommaSeparatedListOutputParser,OutputFixingParser,PydanticOutputParser
)
from langchain.agents import (
    Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
)
