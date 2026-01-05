import os
import re
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest
from pathlib import Path
import uuid

def extract_chapter_info(file_path):
    """Extract chapter information from file path and content"""
    path = Path(file_path)

    # Extract chapter number and title from filename or content
    chapter_match = re.search(r'chapter(\d+)', path.name, re.IGNORECASE)
    chapter_num = chapter_match.group(1) if chapter_match else "unknown"

    # Try to extract title from the first heading in the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(500)  # Read first 500 chars to find title
            title_match = re.search(r'#\s+(.+?)(?:\n|$)', content)
            title = title_match.group(1) if title_match else path.stem
    except:
        title = path.stem

    return f"Chapter {chapter_num}", title

def main():
    """
    Main function to load, split, and store documents in Qdrant.
    """
    # Define constants
    ABS_PATH = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(ABS_PATH, "../physical-ai-book/docs")

    # Initialize Qdrant client (try local first, fallback to in-memory for testing)
    try:
        qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_HOST", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
            prefer_grpc=False
        )
        print("Connected to Qdrant server.")
    except Exception as e:
        print(f"Could not connect to Qdrant server: {e}")
        print("Starting in-memory Qdrant for testing...")
        qdrant_client = QdrantClient(":memory:")  # In-memory for testing
        print("Using in-memory Qdrant instance.")

    COLLECTION_NAME = "physical_ai_book"

    # Create collection if it doesn't exist
    try:
        qdrant_client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        # If collection exists, we need to delete it to recreate with correct dimensions
        qdrant_client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection to recreate with correct dimensions.")
    except:
        pass  # Collection doesn't exist, will create it

    print(f"Creating collection '{COLLECTION_NAME}'...")
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),  # Using smaller model size
    )
    print(f"Collection '{COLLECTION_NAME}' created successfully.")

    # Load documents
    print("Loading documents...")
    loader = DirectoryLoader(DATA_DIR, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents.")

    # Split documents
    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} text chunks.")

    # Create embeddings using a local model
    print("Creating embeddings with local model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Prepare points for Qdrant
    points = []
    for i, doc in enumerate(texts):
        # Extract chapter information
        chapter, title = extract_chapter_info(doc.metadata.get('source', ''))

        # Create embedding
        embedding = embeddings.embed_query(doc.page_content)

        # Create Qdrant point
        point = rest.PointStruct(
            id=str(uuid.uuid4()),  # Generate unique ID
            vector=embedding,
            payload={
                "text": doc.page_content,
                "chapter": chapter,
                "title": title,
                "heading": doc.metadata.get('heading', ''),
                "file_path": doc.metadata.get('source', ''),
                "page_number": doc.metadata.get('page', 0),
                "chunk_id": f"chunk_{i}"
            }
        )
        points.append(point)

    # Upload to Qdrant in batches
    print("Uploading to Qdrant...")
    batch_size = 10  # Process in smaller batches to avoid memory issues

    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch
        )
        print(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")

    print(f"Successfully ingested {len(texts)} document chunks into Qdrant collection '{COLLECTION_NAME}'")
    print("Data ingestion completed successfully!")

if __name__ == "__main__":
    main()
