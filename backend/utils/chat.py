import time
import uuid
import os

import psycopg
from . import llm
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from dotenv import load_dotenv


load_dotenv(".env")
conn_info = f"dbname=langchaindb user=admin password={os.getenv('POSTGRES_PASSWORD')} host=localhost port=5432"
sync_connection = psycopg.connect(conn_info)

chat_history_table = "chat_history"

class ChatBot:
    def __init__(self, session_id):
        self.llm = llm
        # create the chat history table - double check if it exists
        PostgresChatMessageHistory.create_tables(sync_connection, chat_history_table)
        
        self.chat_history = PostgresChatMessageHistory(
            chat_history_table,
            session_id, # session_id
            sync_connection=sync_connection
        )
        
        # Add some messages to the chat history
        self.chat_history.add_messages([
            SystemMessage(content="System message example"),
            AIMessage(content="AI message example"),
            HumanMessage(content="Human message example"),
        ])
        
        print(self.chat_history.get_messages())
    
    def invoke(self, text: str) -> str:
        """invokes the model with the given text

        Args:
            text(str): input text or prompt

        Returns:
            str: response from the model
        """
        
        response = self.llm.invoke(input=text)
        
        return response.content
    
    def stream_invoke(self, text: str):
        """invokes the model with the given text with streaming

        Args:
            text(str): input text or prompt

        Returns:
            str: streams the response from the model
        """
        
        for chunk in self.llm.stream(input=text):
            yield chunk.content
    
    
        