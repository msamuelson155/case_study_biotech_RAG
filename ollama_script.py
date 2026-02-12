import os
import chromadb
import ollama
from sentence_transformers import SentenceTransformer

#setup engine
print("Initializing Clinical Sentinel (AMD Optimized)...")
model = SentenceTransformer(
    "all-MiniLM-L6-v2", 
    backend="onnx",
    model_kwargs={"provider": "DmlExecutionProvider"}
)

def biotech_rag_system(user_query):
    #connect to Chroma DB (vector DB)
    base_dir = r"C:\Users\Owner\Documents\python_work\case_study_biotech_RAG"
    db_path = os.path.join(base_dir, "data", "vector_db")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name="clinical_trials")

    #semantic retrieval
    results = collection.query(query_texts=[user_query], n_results=3)
    
    #prepare context for LLM answer generation
    context_chunks = []
    
    #grab documents and handle potentially missing metadata
    docs = results.get('documents', [[]])[0]
    metas = results.get('metadatas', [[]])[0] if results.get('metadatas') else []

    for i in range(len(docs)):
        text = docs[i]
        # Use .get() only if the metadata object itself isn't None
        if metas and i < len(metas) and metas[i] is not None:
            src = metas[i].get('source', 'Unknown Document')
        else:
            src = "Archive Document"
        
        context_chunks.append(f"[Source: {src}]\n{text}")
        context_chunks.append(f"[Metadata: {metas[i] if metas and i < len(metas) else 'No Metadata'}]") #consider removing

    full_context = "\n\n---\n\n".join(context_chunks)

    #generate answer using LLAMA 3
    system_prompt = (
        "You are a Senior Clinical Trial Auditor. Answer the query based ONLY on the context. "
        "At the end of your answer, list the 'Evidence Sources' used."
    )
    
    response = ollama.generate(
        model='llama3',
        system=system_prompt,
        prompt=f"Context:\n{full_context}\n\nQuestion: {user_query}"
    )

    print("\n" + "="*50)
    print("AUDIT REPORT")
    print("="*50)
    print(response['response'])

if __name__ == "__main__":
    query = "Summarize the exclusion criteria for patients with current infections or fever."
    biotech_rag_system(query)