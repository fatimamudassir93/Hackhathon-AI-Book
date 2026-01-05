"""
Inspect the points that are missing content and source fields
"""
from qdrant_setup import get_qdrant_client, COLLECTION_NAME

client = get_qdrant_client()

# Get 10 points to find the problematic ones
result = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=10,
    with_payload=True,
    with_vectors=False
)

if result and result[0]:
    points = result[0]
    print(f"Inspecting {len(points)} points:\n")

    for i, point in enumerate(points):
        has_content = 'content' in point.payload
        has_source = 'source' in point.payload

        print(f"Point {i}:")
        print(f"  ID: {point.id}")
        print(f"  Has 'content': {has_content}")
        print(f"  Has 'source': {has_source}")
        print(f"  All keys: {list(point.payload.keys())}")

        if not has_content or not has_source:
            print(f"  PROBLEMATIC POINT - Payload dump:")
            for key, value in point.payload.items():
                value_str = str(value)[:100] if len(str(value)) > 100 else str(value)
                print(f"    {key}: {value_str}")
        print()
else:
    print("No points found")
