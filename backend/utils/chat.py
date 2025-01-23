import time
import uuid
import os

import psycopg
from yaml import serialize
from . import llm
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
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

prompt = ChatPromptTemplate.from_messages(
        [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ]
)

        
def serialize_message(message):
    """
    Serialize a message to a dictionary that can be JSON serialized
    
    Args:
        message (BaseMessage): Message to serialize
    
    Returns:
        dict: Serialized message
    """
    
    serialized = {
        'type': message.__class__.__name__, 
        'content': message.content,
        'additional_kwargs': message.additional_kwargs,
        'id': str(message.id) if message.id else None
    }
    
    return serialized

def deserialize_message(serialized_message):
    """
    Deserialize a message from a dictionary
    
    Args:
        serialized_message (dict): Serialized message
    
    Returns:
        BaseMessage: Deserialized message
    """
    message_type = serialized_message['type']
    
    if message_type == 'HumanMessage':
        return HumanMessage(
            content=serialized_message['content'],
            additional_kwargs=serialized_message.get('additional_kwargs', {}),
            id=serialized_message.get('id')
        )
    elif message_type == 'AIMessage':
        return AIMessage(
            content=serialized_message['content'],
            additional_kwargs=serialized_message.get('additional_kwargs', {}),
            response_metadata=serialized_message.get('response_metadata', {}),
            id=serialized_message.get('id'),
            usage_metadata=serialized_message.get('usage_metadata')
        )
    elif message_type == 'SystemMessage':
        return SystemMessage(
            content=serialized_message['content'],
            additional_kwargs=serialized_message.get('additional_kwargs', {}),
            id=serialized_message.get('id')
        )
    else:
        raise ValueError(f"Unknown message type: {message_type}")



class ChatBot:
    def __init__(self):
        self.llm = llm
        
        # Create the chat history table
        PostgresChatMessageHistory.create_tables(sync_connection, chat_history_table)
        
        self.chain = prompt | self.llm
        self.chain_with_history = RunnableWithMessageHistory(
            self.chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        return PostgresChatMessageHistory(
            chat_history_table,
            session_id,
            sync_connection=sync_connection
        )
        
    def get_message_history(self, session_id:str):
        session_history = self.get_session_history(session_id)
        messages = [serialize_message(message) for message in session_history.get_messages()]
        
        # Format the messages for the response
        formatted_messages = [
            {
                "id": str(index + 1),
                "role": "user" if message['type'] == 'HumanMessage' else "assistant",
                "content": message['content']
            }
            for index, message in enumerate(messages)
        ]
        
        # print(f"Formatted Messages: {formatted_messages}")
        
        return formatted_messages

    def run_with_history(self, input: str, session_id: str) -> str:
        """
        Runs the chatbot with intelligent history handling
        
        Args:
            input (str): User's input message
            session_id (str): Unique identifier for the session
        
        Returns:
            str: AI's response
        """
        try:
            response = self.chain_with_history.invoke(
                {"input": input},
                config={"configurable": {"session_id": session_id}}
            )
            
            return response.content
        
        except Exception as e:
            print(f"Error in run_with_history: {e}")
            # Fallback to simple invoke
            return self.llm.invoke(input)
    
    def stream_invoke(self, text: str, session_id: str):
        """Invokes the model with the given text with streaming

        Args:
            text (str): Input text or prompt
            session_id (str): Unique identifier for the session

        Yields:
            str: Streams the response from the model
        """
        session_history = self.get_session_history(session_id)
        messages = session_history.get_messages()
        
        for chunk in self.llm.stream(input=messages):
            yield chunk.content