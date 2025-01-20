from . import llm
import time

class ChatBot:
    def __init__(self):
        self.llm = llm
    
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
        