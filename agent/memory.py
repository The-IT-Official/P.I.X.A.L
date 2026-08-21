import chromadb
import uuid
from langchain_core.tools import tool

chroma_client = chromadb.PersistentClient(path='./neuroforge_memory')

collection = chroma_client.get_or_create_collection(name="neuroforge_memory")

@tool
def remember(text, metadata):
    """Stores a memory about a completed task, error, or decision with flexible metadata."""
    collection.add(
        ids=[str(uuid.uuid4())],
        documents=[text],
        metadatas=[metadata]
    )
    return f"Memory stored: {text[:50]}..."

@tool
def recall(query, n_results = 3):
    """Searches past memories semantically similar to the query and returns them."""
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = results['documents'][0]
    if not docs:
        return "No relevant memories found."
    return "\n".join(docs)

@tool
def forget(memory_id):
    """Deletes a specific memory by its ID."""
    collection.delete(ids=[memory_id])
    return f"Memory {memory_id} deleted."

memory_tools = [remember, recall, forget]

# test at bottom of memory.py
if __name__ == "__main__":
    print(remember.invoke({"text": "Built Flask API, fixed CORS with flask-cors", "metadata": {"type": "task", "status": "success"}}))
    print(recall.invoke({"query": "Flask API"}))