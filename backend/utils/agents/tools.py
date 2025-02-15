from langchain_core.tools import tool


# @tool
# def code_retriever():
#     ...
    
# @tool
# def csv_retriever():
#     ...
    
# @tool
# def document_retriever():
#     ...
    
@tool
def search(query: str):
    """Call to surf the web."""
    # This is a placeholder, but don't tell the LLM that...
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."