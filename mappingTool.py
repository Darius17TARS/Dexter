import json
from typing import Dict, List, Union, Tuple, Any
import logging

# Define the internal permission levels
INTERNAL_LEVELS = {
    "Pflegedienstleitung": 6,
    "PDL": 6,
    "Einrichtungsleitung": 6,
    "Wohnbereichsleitung": 6,
    "WBL": 6,
    "Pflegefachkraft": 6,
    "PFK": 6,
    "Pflegeassistenzkraft": 4,
    "Pflegehilfskraft": 3,
    "Azubi 3. Lehrjahr": 4,
    "Azubi": 3,
    "Auszubildende": 3,
    "Betreuungskraft": 2,
    "Sozialer Dienst": 2,
    "Verwaltungskraft": 0,
    "Hauswirtschaftshilfe": 0
}

# The boolean returned is for tagging a possible semantic problem with roles.
def map_permission(external_role: Union[str, None]) -> Tuple[int, bool]:
    if external_role is None:
        return 0, False
    
    normalized_role = external_role.lower().strip()

    for role, level in INTERNAL_LEVELS.items():
        if normalized_role == role.lower():
            return level, False
        
    # You can also do a partial search but in my opinion this can
    # be really insecure:
    for role, level in INTERNAL_LEVELS.items():
        if role.lower() in normalized_role:
            return level, True
        
    logging.warning(f"Unmapped role encountered: {external_role}. Defaulting to NONE permission level.")
    return 0, False

def process_type1(data: List[Dict[str, Union[str, None]]]) -> List[Dict[str, Union[str, int, bool]]]:
    mapped_data = []
    for nurse in data:
        external_role = nurse.get("bezeichnung")
        try:
            internal_level, revision_flag = map_permission(external_role)
            mapped_data.append({
                "external_role": external_role,
                "internal_level": internal_level,
                "role_found_w_partial_search": revision_flag
            })
    
        except Exception as e:
            logging.error(f"Error processing nurse data: {nurse}. Error: {str(e)}")

    return mapped_data

def process_type2(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    mapped_data = []

    for nurse in data:
        external_role = nurse.get("qualifikation")

        try:
            internal_level, revision_flag = map_permission(external_role)
            mapped_data.append({
                "external_role": external_role,
                "internal_level": internal_level,
                "role_found_w_partial_search": revision_flag,
                "additional_info": {
                    key: value for key, value in nurse.items()
                    if key != "qualifikation"
                }
            })

        except Exception as e:
            logging.error(f"Error processing nurse data: {nurse}. Error: {str(e)}")

    return mapped_data

def identify_json_type(data: List[Dict[str, Any]]) -> str:
    if not data:
        raise ValueError("Empty data provided")
    
    sample = data[0]

    if "bezeichnung" in sample:
        return "type1"
    elif "qualifikation" in sample:
        return "type2"
    else:
        raise ValueError(f"Unknown data structure: {sample.keys()}")

#check what structure the element has, 1 or 2.
def process_nursing_home(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    json_type = identify_json_type(data)
    if json_type == "type1":
        return process_type1(data)
    elif json_type == "type2":
        return process_type2(data)
    else:
        raise ValueError("Unknown JSON structure")

def main(jsonpath: json):
    try:
        with open(jsonpath, "r") as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            raise ValueError("Input JSON should be a dictionary with nursing homes as keys")
        
        results = {}
        for home, home_data in data.items():
            try:
                results[home] = process_nursing_home(home_data)
                logging.info(f"Successfully processed {home}")
            except Exception as e:
                logging.error(f"Error processing {home}: {str(e)}")
                results[home] = []
        
        with open("mapped_permissions.json", "w") as f:
            json.dump(results, f, indent=3)
        
        logging.info("Mapping complete. Results saved to 'mapped_permissions.json'")
    except Exception as e:
        logging.error(f"An error occurred in main execution: {str(e)}")

if __name__ == "__main__":
    main("sample-nursing-homes-data.json")