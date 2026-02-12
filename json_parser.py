import json  
import os    

def parse_eligibility():
    base_dir = r"C:\Users\Owner\Documents\python_work\case_study_biotech_RAG"  
    raw_path = os.path.join(base_dir, "data", "raw", "NCT04470427.json")       
    output_dir = os.path.join(base_dir, "data", "processed")                   
    
    if not os.path.exists(raw_path):  #prevent from opening file that doesnt exist
        print(f"Could not find raw JSON at {raw_path}") 
        return #exist rest of the function if file not found

    with open(raw_path, 'r', encoding='utf-8') as f:  #read file at raw path ("r") and alias as f 
        data = json.load(f)  

    try:  
        criteria = data["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]  #establish criteria to search using keywords from json
        
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "moderna_criteria.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:  #write extracted criteria to new file ("w")
            f.write(criteria)
            
        print(f"Successfully extracted criteria to {output_path}")

    except KeyError as e:
        print(f"Parsing error: Key {e} not found.")

if __name__ == "__main__":
    parse_eligibility()