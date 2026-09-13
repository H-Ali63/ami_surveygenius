import os
import requests
from datetime import datetime, timedelta
from django.conf import settings
from search.models import AccessToken


def fetch_token_from_api():
    
    try:
        # Example API provider's refresh endpoint
        refresh_url = "https://api.axismyindia.in/v1/user/partner"
        headers = {"refresh_token":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoiUUMxNzM2OTMyNDY3OTkxSVQiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczNjkzMjQ2N30.vi--6USBoZlvpHGV12IjXNqG8j6q78ZOqEnuORfhE7M","accept":"application/json","locale":"en"}
        response = requests.patch(refresh_url, headers=headers)
        print(response,">>>>")
        if response.status_code == 200:
            data = response.json()
            print(data)
            new_token = data['data']["access_token"]
            if not new_token:
                raise ValueError("No token returned from the API.")
            else:
                return new_token
        else:
            raise Exception(f"Failed to refresh API key. Status Code: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error refreshing API key: {str(e)}")
        raise

# Automatically Refresh API Key if Expired
def refresh_api_key():
    """
    Fetch an existing token or refresh it if invalid.
    """
    # token_instance = AccessToken.get_existing_token()
 
    # if token_instance:
    #     return token_instance.token
 
    # If no token exists, fetch a new one
    new_token = fetch_token_from_api()
    AccessToken.save_new_token(new_token)
    return new_token
