from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, CSVLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from dotenv import load_dotenv
import logging
import os

load_dotenv("../.env")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

embeddings = OllamaEmbeddings(model="nomic-embed-text")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class VectorStore:
    def __init__(self):
        self.connection = f"postgresql+psycopg://admin:langchain_123@localhost:5432/langchaindb"
        self.docs_collection = "docsCollection"
        self.code_collection = "codeCollection"
        self.csv_collection = "csvCollection"
        
        self.docs_vector_store = PGVector(
            connection=self.connection,
            collection_name=self.docs_collection,
            embeddings=embeddings,
        )
        
        self.code_vector_store = PGVector(
            connection=self.connection,
            collection_name=self.code_collection,
            embeddings=embeddings,
        )
        
        self.csv_vector_store = PGVector(
            connection=self.connection,
            collection_name=self.csv_collection,
            embeddings=embeddings,
        )
    
    def add_document_pdf(self, document_path: str):
        loader = PyPDFLoader(document_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        all_splits = text_splitter.split_documents(docs)
        
        try:
            for split in all_splits:
                self.docs_vector_store.add_documents(split)
        except Exception as e:
            logger.info(f"Error adding document to vector store: {e}")
    
    def add_document_code(self, file_path: str):
        loader = GenericLoader.from_filesystem(
            file_path,
            glob="*",
            suffixes=[".cpp", ".py", ".js"],
            parser=LanguageParser()
        )
        docs = loader.load()
        try:
            for doc in docs:
                print(doc)
                self.code_vector_store.add_documents(doc)
        except Exception as e:
            logger.info(f"Error adding code to vector store: {e}")
    
    def add_document_csv(self, file_path: str):
        """
        Adds a CSV file to the PGVector collection.

        Args:
            file_path (str): Path to the CSV file.
        """
        loader = CSVLoader(file_path)
        docs = loader.load()
        try:
            for doc in docs:
                self.csv_vector_store.add_documents(doc)
        except Exception as e:
            logger.info(f"Error adding csv to vector store: {e}")

    def get_retriever(self, store_type: str = "docs", k: int = 5):
        """
        Returns a retriever for the specified collection.

        Args:
            store_type (str): Which vector store to use. Options: 'docs', 'code', 'csv'.
            k (int): Number of top results to return for a query.

        Returns:
            A retriever instance ready for use in a LangGraph node.
        """
        if store_type == "docs":
            return self.docs_vector_store.as_retriever(search_kwargs={"k": k})
        elif store_type == "code":
            return self.code_vector_store.as_retriever(search_kwargs={"k": k})
        elif store_type == "csv":
            return self.csv_vector_store.as_retriever(search_kwargs={"k": k})
        else:
            logger.error(f"Invalid store type: {store_type}. Valid options are 'docs', 'code', or 'csv'.")
            raise ValueError(f"Invalid store type: {store_type}. Valid options are 'docs', 'code', or 'csv'.")


if __name__ == "__main__":
    vector_store = VectorStore()
    vector_store.add_document_code("../../uploads/main.py")
    vector_store.code_vector_store.similarity_search("starting_fen", k=10)
