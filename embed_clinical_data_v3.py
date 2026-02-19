import os  
import chromadb 
import ollama

#configure directories
base_dir = r"C:\Users\Owner\Documents\python_work\case_study_biotech_RAG"
db_path = os.path.join(base_dir, "data", "vector_db")
report_dir = os.path.join(base_dir, "audit_reports")

#connect to vector db
client = chromadb.PersistentClient(path=db_path)

#access extracted text from clinical protocol pdf 
protocol_col = client.get_collection(name="clinical_protocols")

#access extracted json
results_col = client.get_collection(name="clinical_results")

#define function to perform audit comparison
def run_alignment_audit(query, report_name="regulatory_alignment_report.txt"):
    print(f"\n--- Analyzing Regulatory Alignment: {query} ---")
    
    #query PDF collection. pull top 8 most relevant text chunks
    rule_results = protocol_col.query(query_texts=[query], n_results=8)
    #merge chunks into one string for model to read
    rules_text = "\n".join(rule_results['documents'][0])
    
    data_results = results_col.query(query_texts=[query], n_results=15)
    data_text = "\n".join(data_results['documents'][0])
    
    #context injection. creates a prompt combining the rules and the data
    prompt = f"""
    ROLE: Regulatory Compliance Auditor
    TASK: Compare the Reporting Plan (Protocol) against the Final Published Results (JSON).
    
    [PROTOCOL SECTION]:
    {rules_text}
    
    [JSON RESULTS SECTION]:
    {data_text}
    
    QUESTION: {query}
    
    INSTRUCTIONS:
    1. Identify the 'Timeframe' or 'Definition' required by the Protocol.
    2. Check the JSON section for the 'timeFrame' or 'description' fields.
    3. State if the Final Results match the Protocol's requirements.
    4. If the JSON uses a shorter timeframe than the Protocol required, flag it as a 'REPORTING DEVIATION'.
    """
    
    #send prompt to the model for analysis
    response = ollama.generate(model='llama3', prompt=prompt)
    #extract response from model
    report_body = response['response']

    #output audit report file
    full_report_path = os.path.join(report_dir, report_name)
    with open(full_report_path, "w", encoding="utf-8") as f:
        f.write("REGULATORY ALIGNMENT AUDIT\n") #header
        f.write("="*30 + "\n") #line break formatting
        f.write(report_body) #write model-generated findings
    
    print(f"\nAlignment report saved to {full_report_path}")

#ensures the script only runs if executed directly
if __name__ == "__main__":
    run_alignment_audit("What is the timeframe for reporting unsolicited adverse events, and does the JSON results module follow this?")