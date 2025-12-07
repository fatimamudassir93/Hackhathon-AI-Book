import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Set up environment variables
os.environ["OPENAI_API_KEY"] = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Define constants
ABS_PATH = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "db")
DATA_DIR = os.path.join(ABS_PATH, "../../physical-ai-book/docs")

def main():
    """
    Main function to load, split, and store documents.
    """
    # Load documents
    loader = DirectoryLoader(DATA_DIR, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # Create and store embeddings
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    vectorstore.persist()

if __name__ == "__main__":
    main()
