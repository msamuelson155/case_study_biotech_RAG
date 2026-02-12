import chromadb #vector db library
import os

def setup_db():
    base_dir = r"C:\Users\Owner\Documents\python_work\case_study_biotech_RAG"
    db_path = os.path.join(base_dir, "data", "vector_db")
    
    #initialize the Chroma Client - 'PersistentClient' ensures the data stays ie. after power cut etc
    client = chromadb.PersistentClient(path=db_path)
    
    #create a 'Collection' - which is basically like a table in a db
    collection = client.get_or_create_collection(name="clinical_trials")
    
    print(f"ChromaDB initialized at: {db_path}")
    print(f"Collection 'clinical_trials' is ready for data.")

if __name__ == "__main__":
    setup_db()