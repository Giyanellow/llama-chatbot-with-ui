from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, CSVLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

embeddings = OllamaEmbeddings(model="llama3.2")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 0



class VectorStore:
    def __init__(self):
        self.connection = "postgresql+psycopg://admin:langchain_123@localhost:5432/langchaindb"
        self.docs_collection = "docsCollection"
        self.code_collection="codeCollection"
        self.csv_collection="csvCollection"
        
        self.docs_vector_store = PGVector(
            connection=self.connection,
            collection=self.docs_collection,
            embeddings=embeddings,
        )
        
        self.code_vector_store = PGVector(
            connection=self.connection,
            collection=self.code_collection,
            embeddings=embeddings,
        )
        
        self.csv_vector_store = PGVector(
            connection=self.connection,
            collection=self.csv_collection,
            embeddings=embeddings,
        )
        
        
    
    def add_document_pdf(self, document_path: str):
        loader = PyPDFLoader(document_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Adjust based on your needs
            chunk_overlap=200,  # Helps maintain context between chunks
            add_start_index=True  # Preserves original document context
        )

        # Split the documents
        all_splits = text_splitter.split_documents(docs)
        
        try:
            # Add the splits to the vector store
            for split in all_splits:
                self.docs_vector_store.add_document(split)
            
        except Exception as e:
            logger.info(f"Error adding document to vector store: {e}")
    
    def add_document_code(self, file_path: str):
        loader = GenericLoader.from_filesystem(file_path,
                                               glob="*",
                                               suffixes=[".cpp", ".py", ".js"],
                                               parser=LanguageParser())
        docs = loader.load()
        
        try:
            for doc in docs:
                self.code_vector_store.add_document(doc)
                
        except Exception as e:
            logger.info(f"Error adding code to vector store: {e}")
    
    def add_document_csv(self, file_path: str):
        loader = CSVLoader(file_path)
        docs = loader.load()
        
        try:
            for doc in docs:
                self.csv_vector_store.add_document(doc)
        
        except Exception as e:
            logger.info(f"Error adding csv to vector store: {e}")