from langchain_core.tools import tool

from .embeddings import VectorStore

vector_db = VectorStore()

@tool
def code_retriever_tool(query: str) -> str:
    """
    Retrieves relevant code snippets from the vector database based on the query.

    Args:
        query (str): The query to search for.

    Raises:
        ValueError: If there is an error retrieving the code.

    Returns:
        str: The relevant code snippets.
    """
    try:
        retriever = vector_db.get_retriever(store_type="code")
        docs = retriever.get_relevant_documents(query, k=5)
        
        return "\n\n".join(doc.page_content for doc in docs)
    
    except Exception as e:
        raise ValueError(f"Error retrieving code: {e}")

@tool
def csv_retriever_tool(query: str) -> str:
    """
    Retrieves relevant content from CSV files in the vector database based on the query.

    Args:
        query (str): The query to search for.

    Raises:
        ValueError: If there is an error retrieving the CSV.

    Returns:
        str: The relevant CSV content.
    """
    try:
        retriever = vector_db.get_retriever(store_type="csv")
        docs = retriever.get_relevant_documents(query, k=5)
        
        return "\n\n".join(doc.page_content for doc in docs)

    except Exception as e:
        raise ValueError(f"Error retrieving csv: {e}")
    
@tool
def doc_retriever_tool(query: str) -> str:
    """
    Retrieves relevant document content from the vector database based on the query.

    Args:
        query (str): The query to search for.

    Raises:
        ValueError: If there is an error retrieving the documents.

    Returns:
        str: The relevant document content.
    """
    try:
        retriever = vector_db.get_retriever(store_type="doc")
        docs = retriever.get_relevant_documents(query, k=5)
        
        return "\n\n".join(doc.page_content for doc in docs)
    
    except Exception as e:
        raise ValueError(f"Error retrieving documents: {e}")
    