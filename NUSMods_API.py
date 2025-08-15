import requests

'''
    1) This script interacts with NUSMods API;
    2) Documentation: https://api.nusmods.com/v2/#/
    3) This script is imported as a module.
'''

def fetch_nusmods_data(endpoint, acadYear, moduleCode=None, semester=None):
    """
    Fetches data from the NUSMods API.
    
    Parameters:
        endpoint (str): The API endpoint to fetch data from;
            { 
                moduleList = fetches summaries of all modules,
                moduleInfo = fetches detailed information about all modules,
                module = fetches detailed information about specific module,
                venues = fetches all venues,
                venueInfo = fetches detailed information about all venues
            }
        acadYear (e.g '2024-2025'): The academic year (e.g., '2024-2025').
        moduleCode (e.g 'DAO1704'): The module code (only for module-specific endpoints).
        semester (e.g 1): The semester number (only for semester-specific endpoints).

    """
    base_url = f"https://api.nusmods.com/v2/{acadYear}"

    if endpoint == "moduleList":
        url = f"{base_url}/moduleList.json"
    elif endpoint == "moduleInfo":
        url = f"{base_url}/moduleInfo.json"
    elif endpoint == "module":
        if not moduleCode:
            raise ValueError("Module code is required for module endpoint")
        url = f"{base_url}/modules/{moduleCode}.json"
    elif endpoint == "venues":
        if not semester:
            raise ValueError("Semester is required for venues endpoint")
        url = f"{base_url}/semesters/{semester}/venues.json"
    elif endpoint == "venueInfo":
        if not semester:
            raise ValueError("Semester is required for venueInfo endpoint")
        url = f"{base_url}/semesters/{semester}/venueInformation.json"
    else:
        raise ValueError("Invalid endpoint")
    
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response

def get_module_description(moduleCode, acadYear="2024-2025"):

    response = None

    ''' ========================= 
    1) try fetching raw data from API, raise any exceptions if failed: 
    ======================== '''

    try:
        response = fetch_nusmods_data(endpoint='module', acadYear=acadYear, moduleCode=moduleCode)
        raw = response.json()
    except requests.exceptions.HTTPError as e:
        if response and response.status_code == 404: 
            print(f"HTTP 404 Error: The requested resource was not found for {moduleCode}")
        else:
            print(f"HTTP error {response.status_code if response else 'Unknown'} for {moduleCode} " + f"{e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching {moduleCode} " + f"{str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error while fetching {moduleCode} " + f"{str(e)}")
        return None
    
    ''' ========================= 
    2) if raw data successfully fetched, try obtain relevant path data:
    ======================== '''

    # check if module description exists:
    if not raw.get("description"):
            print(f"No description available for {moduleCode}")
            return None
    else:
        description = raw.get("description")
        return description
    