from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv(".env")

llm = ChatOllama(
    model=str(os.getenv("OLLAMA_MODEL")),
    temperature = 0.7,
)