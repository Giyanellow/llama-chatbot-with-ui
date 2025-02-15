"""
Helper functions for the backend.
"""


def parse_history(chat_history: list) -> dict:
    """
    Parse the chat history into a dictionary of messages.
    """
    messages = {}
    for message in chat_history:
        if message.__class__.__name__ == "HumanMessage":
            messages["user"] = message.content
        elif message.__class__.__name__ == "AIMessage":
            messages["bot"] = message.content
    return messages