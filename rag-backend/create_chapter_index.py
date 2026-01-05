"""
Create payload index for chapter field in Qdrant
Required for chapter-based filtering
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

load_dotenv()

print("Creating chapter index in Qdrant...")
print("-" * 80)

# Connect to Qdrant
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "physical_ai_book")

try:
    # Create payload index for 'chapter' field
    qdrant_client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="chapter",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print(f"[OK] Created keyword index for 'chapter' field")
    print(f"     Collection: {COLLECTION_NAME}")
    print(f"     Field: chapter")
    print(f"     Type: KEYWORD")
    print()
    print("[OK] Chapter filtering is now enabled!")

except Exception as e:
    if "already exists" in str(e).lower():
        print(f"[OK] Index for 'chapter' already exists")
    else:
        print(f"[ERROR] Failed to create index: {e}")
        raise

print("-" * 80)
