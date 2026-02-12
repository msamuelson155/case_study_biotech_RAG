import os
import chromadb
from sentence_transformers import SentenceTransformer

def query_clinical_trials(user_query, source_filter=None):
    """
    Optimized search function with Metadata Filtering.
    :param user_query: The natural language question.
    :param source_filter: Optional string to filter by trial (e.g., 'moderna_nct04470427')
    """
    print("--- Clinical Sentinel: Advanced Search (AMD GPU) ---")
    
    base_dir = r"C:\Users\Owner\Documents\python_work\case_study_biotech_RAG"
    db_path = os.path.join(base_dir, "data", "vector_db")

    #initialize the ChromaDB client and connect
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name="clinical_trials")

    #ONNX + DIRECTML ENGINE
    print("🚀 Connecting to DirectML Execution Provider...")
    model = SentenceTransformer(
        "all-MiniLM-L6-v2", 
        backend="onnx",
        model_kwargs={"provider": "DmlExecutionProvider"}
    )

    #prep the filter so that ChromaDB can use to exclude irrelevant documents and narrow results
    where_clause = {"source": source_filter} if source_filter else None

    #semantic search execution
    print(f"Querying: '{user_query}'")
    if source_filter:
        print(f"Filter Applied: Source = {source_filter}")

    #optional metadata filter
    results = collection.query(
        query_texts=[user_query],
        n_results=3,
        where=where_clause 
    )

    #results
    print("\n" + "="*60)
    print(f"TOP CLINICAL MATCHES")
    print("="*60)

    #check to find matching criteria
    if not results['documents'][0]:
        print("No matching criteria found for this query.")
        return

    for i in range(len(results['documents'][0])):
        content = results['documents'][0][i]
        distance = results['distances'][0][i]
        metadata = results['metadatas'][0][i]
        
        #convert distance to a readable confidence score
        #1.0 = perfect match; < 0.7 indicates a loose connection
        confidence = 1 - distance
        
        print(f"MATCH {i+1} | Confidence: {confidence:.4f} | Source: {metadata.get('source')}")
        print(f"CONTENT: {content[:500]}...") #truncate text for clean previewoutput
        print("-" * 30)

if __name__ == "__main__":
    #ex use case:
    test_question = "What are the exclusion criteria regarding fever and body temperature?"
    
    #try running with the filter set up in the ingestion script
    query_clinical_trials(test_question, source_filter="moderna_nct04470427")