import logging
import os
import requests  #type: ignore
from datetime import datetime, timedelta
from django.conf import settings #type: ignore

logger = logging.getLogger(__name__)


def is_api_key_expired():
    return datetime.now() >= settings.API_KEY_EXPIRATION

def refresh_api_key():
    try:
        refresh_url = "https://api.axismyindia.in/v1/user/partner"
        headers = {"refresh_token": os.environ.get("QC_API_REFRESH_TOKEN"), "accept": "application/json", "locale": "en"}
        response = requests.patch(refresh_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            settings.API_KEY = data['data']["access_token"]
            settings.API_KEY_EXPIRATION = datetime.now() + timedelta(days=2)
            logger.info("API key refreshed successfully.")
        else:
            raise Exception(f"Failed to refresh API key. Status Code: {response.status_code}")

    except Exception:
        logger.exception("Error refreshing API key.")
        raise

# Automatically Refresh API Key if Expired
def refresh_api_key_if_expired():
    if is_api_key_expired():
        refresh_api_key()


# Schedule the API key refresh check to run every hour
import threading
def schedule_api_key_refresh():
    refresh_api_key_if_expired()
    threading.Timer(3600, schedule_api_key_refresh).start()  # Run every hour