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

system_prompt = """
    You are an assistant that helps users with understanding Harry Potter books. 
    Your main task is to answer any questions that the user may have regarding Harry Potter and its universe.

    Reminders:
        Always remember to be kind, respectful and enthusiastic with your messages.
        Never communicate negative or harmful messages.
    
    DO NOT answer any questions that are not related to Harry Potter or its universe.
    
    Output:
        Always format your output in proper markdown format.
"""

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
        
    def get_message_history(self):
        """gets the message history from the chat history
        
        Returns:
            list: list of messages
        """
        
        return self.chat_history.get_messages()
        
    
    def invoke(self, text: str) -> str:
        """invokes the model with the given text

        Args:
            text(str): input text or prompt

        Returns:
            str: response from the model
        """
        
        messages = self.chat_history.get_messages()
        messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=text))
        
        response = self.llm.invoke(input=messages)
        
        return response.content
    
    def stream_invoke(self, text: str):
        """invokes the model with the given text with streaming

        Args:
            text(str): input text or prompt

        Returns:
            str: streams the response from the model
        """
        
        messages = self.chat_history.get_messages()
        messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=text))
        
        for chunk in self.llm.stream(input=messages):
            yield chunk.content
    
    
        