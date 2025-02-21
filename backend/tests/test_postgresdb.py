import os
import sys
import uuid
from dotenv import load_dotenv

# Add the parent directory and utils directory to the sys.path to import utils and agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))

from utils.chat import MessageHistoryDB

# Load environment variables from .env file
load_dotenv()

def test_postgres_chat_message_history():
    # Create a session ID
    session_id = str(uuid.uuid4())
    
    chat_history = MessageHistoryDB(session_id)

    # Create some messages
    human_message = "Hello, how are you?"
    ai_message = "I am an AI, what can I help you with?"

    # Save the messages
    chat_history.add_user_message(message=human_message)
    chat_history.add_bot_message(message=ai_message)

    # Retrieve the messages
    messages = chat_history.retrieve_messages()

    # Print the messages to verify
    for message in messages:
        print(f"{message.__class__.__name__}: {message.content}")

if __name__ == "__main__":
    test_postgres_chat_message_history()