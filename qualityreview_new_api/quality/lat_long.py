import requests #
import pandas as pd
import json

def get_pokemon_info(pokemon_name):
    """
    Fetches information for a specific Pokémon from the PokéAPI and returns a dictionary.
    """
    base_url = f"http://192.168.1.198:8091/{pokemon_name}/2026-03-01/2026-03-16"
    response = requests.get(base_url) #

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.json() # # Convert JSON response to a Python dictionary
    else:
        print(f"Error fetching data: Status code {response.status_code}")
        return None

# List to store the fetched data
api_data_list = []

# Fetch data for a few Pokémon
pokemon_names = ["VBG%20Ram%20G%20Awareness%20survey%20Haryana","VBG%20Ram%20G%20Awareness%20survey%20UP","VBG%20Ram%20G%20Awareness%20Survey%20J&K","VBG%20Ram%20G%20Awareness%20survey%20Jharkhand","VBG%20Ram%20G%20Awareness%20survey%20Telangana","VBG%20Ram%20G%20Awareness%20survey%20Karnataka","VBG%20Ram%20G%20Awareness%20survey%20AP","VBG%20Ram%20G%20Awareness%20survey%20Bihar","VBG%20Ram%20G%20Awareness%20survey%20Kerala","VBG%20Ram%20G%20Awareness%20survey%20MP","VBG%20Ram%20G%20Awareness%20survey%20MH","VBG%20Ram%20G%20Awareness%20survey%20Rajasthan","VBG%20Ram%20G%20Awareness%20survey%20CG","VBG%20Ram%20G%20Awareness%20survey%20UK","VBG%20Ram%20G%20Awareness%20Survey%20Punjab","VBG%20Ram%20G%20Awareness%20survey%20Gujarat","VBG%20Ram%20G%20Awareness%20survey%20Assam"]

for name in pokemon_names:
    print(name)
    data = get_pokemon_info(name)
    print(data)
    if data:
        json_string = json.dumps(data)
        print(json_string)

        # 2. Convert to JSON string (formatted/pretty-printed)
        pretty_json = json.dumps(data, indent=4)
        print(pretty_json)

        # 3. Write dictionary to a JSON file
        with open(f'{name}.json', 'w') as f:
            json.dump(data, f, indent=4)

        df = pd.read_json(f'{name}.json')
        df.to_excel(f'{name}.xlsx', index=False)
# Print the final list of data
# print(api_data_list)
