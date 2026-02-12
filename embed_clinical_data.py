import os
import time
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer

def generate_ids(chunks):
    """
    BEST PRACTICE: Content-Addressing.
    Instead of 'MODERNA_1', we hash the text to create a unique fingerprint.
    This prevents duplicates even if the source file is re-organized.
    """
    return [hashlib.md5(chunk.encode('utf-8')).hexdigest() for chunk in chunks]

def embed_clinical_data():
    print("--- Clinical Sentinel: Professional Ingestion Mode ---")
    
    base_dir = r"C:\Users\Owner\Documents\python_work\case_study_biotech_RAG"
    txt_path = os.path.join(base_dir, "data", "processed", "moderna_criteria.txt")
    db_path = os.path.join(base_dir, "data", "vector_db")

    if not os.path.exists(txt_path):
        print(f"❌ Error: File not found at {txt_path}")
        return

    #strip whitespace and filter out noise
    with open(txt_path, "r", encoding="utf-8") as f:
        text_data = f.read()
    chunks = [c.strip() for c in text_data.split('\n\n') if len(c.strip()) > 20]

    #connection to chromaDB in Datagrip. get_or_create prevents 'Collection Already Exists' errors
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="clinical_trials")

    #model loading - backend="onnx" + DirectML (via 'cuda' alias) bypasses PyTorch bugs on AMD.
    print("Initializing AMD-Optimized ONNX Engine...")
    model = SentenceTransformer(
        "all-MiniLM-L6-v2", 
        backend="onnx",
        model_kwargs={"file_name": "model.onnx"},
        device="cuda" 
    )

    #initialize chunks for vectorization
    print(f"Vectorizing {len(chunks)} chunks on RX 9060 XT...")
    start_time = time.perf_counter()
    
    #model.encode converts text into vectors
    embeddings = model.encode(chunks, show_progress_bar=True)
    
    #generate IDs based on the text content.
    ids = generate_ids(chunks)
    
    #duplicate handling using 'update + insert' - if the ID exists, record updates; if not, it adds.
    collection.upsert(
        documents=chunks,
        embeddings=embeddings.tolist(),
        ids=ids,
        metadatas=[{"source": "moderna_nct04470427"} for _ in chunks] # Adding metadata for filtering
    )

    duration = time.perf_counter() - start_time
    print(f"COMPLETE: {len(chunks)} chunks processed.")
    print(f"Throughput: {len(chunks)/duration:.2f} chunks/sec on GPU.")

if __name__ == "__main__":
    embed_clinical_data()