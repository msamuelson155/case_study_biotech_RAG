import requests  #library for sending HTTP requests. handshake between script and website server
import json      #library for translating json into a python dictionary
import os        #talks to Windows

def fetch_trial_data(nct_id="NCT04470427"): 
    #hit the API
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}" 
    print(f"Ingesting {nct_id}...") 
    
    try:  #blocker to try a pull but not crash if it fails
        response = requests.get(url, timeout=10)  #if server not responding, timeout after 10 sec
        response.raise_for_status()  #checks if the website returns an error. prevent saving an error page as data
        
        #save to raw folder
        os.makedirs('data/raw', exist_ok=True)  #create directory
        with open(f"data/raw/{nct_id}.json", "w") as f:  #open file for writing ("w") 
            json.dump(response.json(), f, indent=4)  #converts python data back to json and saves with indent for readability
        print(f"Saved Raw JSON to data/raw/{nct_id}.json")
        
    except Exception as e:  #catch errors
        print(f"API Error: {e}")

if __name__ == "__main__":
    fetch_trial_data()