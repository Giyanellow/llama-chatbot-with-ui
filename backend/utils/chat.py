import time
import uuid
import os

import psycopg
from yaml import serialize, safe_load as deserialize
from typing import List, Union
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
from utils.agents.agent import agent

load_dotenv()


class ChatBot:
    def __init__(self):
        self.agent = agent

    def run(self, user_input: str, session_id: str) -> str:
        # Prepare a state that includes the new input.
        # Pass the session id in the config so that the MemorySaver loads prior history.
        result = self.agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": session_id}}
        )
        return result["messages"][-1].content

    def stream_invoke(self, user_input: str, session_id: str):
        for chunk in self.agent.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": session_id}}
        ):
            yield chunk["chatbot"]["messages"].content
            
class MessageHistoryDB:
    conn_info = f"dbname=langchaindb user=admin password={os.getenv('POSTGRES_PASSWORD')} host=localhost port=5432"
    sync_connection = psycopg.connect(conn_info)
    table_name = "chat_history"
    def __init__(self, session_id: str):
        PostgresChatMessageHistory.create_tables(self.sync_connection, self.table_name)
        self.db = PostgresChatMessageHistory(
            self.table_name,
            session_id,
            sync_connection=self.sync_connection
        )
        
    def add_user_message(self, message: str):
        self.db.add_user_message(HumanMessage(content=message))
    
    def add_bot_message(self, message: str):
        self.db.add_ai_message(AIMessage(content=message))
    
    def retrieve_messages(self) -> List[Union[HumanMessage, AIMessage]]:
        return self.db.get_messages()

# Example usage:
if __name__ == "__main__":
    chatbot_instance = ChatBot()
    session_id = str(uuid.uuid4())
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = chatbot_instance.stream_invoke(user_input, session_id)
        for chunk in response:
            print(chunk, end='', flush=True)