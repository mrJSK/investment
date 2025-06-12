import os
import time
import hashlib
import requests
import json
from django.core.management.base import BaseCommand
# This is the updated import as per the V3 documentation style
from fyers_apiv3.FyersWebsocket import data_ws
from fundamentals.models import FundamentalsCompany


# --- Helper Functions for Credentials (Unchanged) ---
CREDENTIALS_DIR = "credentials"
ACCESS_TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "access_token.txt")
REFRESH_TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "refresh_token.txt")
CLIENT_ID_FILE = os.path.join(CREDENTIALS_DIR, "client_id.txt")
SECRET_KEY_FILE = os.path.join(CREDENTIALS_DIR, "secret_key.txt")
PIN_FILE = os.path.join(CREDENTIALS_DIR, "pin.txt")
FYERS_REFRESH_ENDPOINT = "https://api-t1.fyers.in/api/v3/validate-refresh-token"

def load_file(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: File not found at {path}. Please create it.")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f: f.write("")
        return ""

def save_file(path, content):
    with open(path, "w") as file:
        file.write(content)
    print(f"Data saved to {path}")

def generate_appIdHash(app_id, app_secret):
    raw_string = f"{app_id}:{app_secret}"
    return hashlib.sha256(raw_string.encode()).hexdigest()

def get_new_access_token_from_refresh():
    print("Attempting to refresh access token...")
    app_id = load_file(CLIENT_ID_FILE)
    app_secret = load_file(SECRET_KEY_FILE)
    pin = load_file(PIN_FILE)

    if not all([app_id, app_secret, pin]):
        print("Error: Missing client_id, secret_key, or pin in credentials directory.")
        return None

    appIdHash = generate_appIdHash(app_id, app_secret)
    refresh_token = load_file(REFRESH_TOKEN_FILE)

    if not refresh_token:
        print("Error: Refresh token not found.")
        return None

    payload = {"grant_type": "refresh_token", "appIdHash": appIdHash, "refresh_token": refresh_token, "pin": pin}

    try:
        resp = requests.post(FYERS_REFRESH_ENDPOINT, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("s") == "ok" and "access_token" in data:
            new_access_token = data["access_token"]
            save_file(ACCESS_TOKEN_FILE, new_access_token)
            if "refresh_token" in data:
                save_file(REFRESH_TOKEN_FILE, data["refresh_token"])
            return new_access_token
        else:
            print(f"Error refreshing token: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"An unexpected error occurred during token refresh: {e}")
        return None

# --- Django Management Command ---

# Global variable to hold the fyers socket object to be accessed in callbacks
fyers = None

class Command(BaseCommand):
    help = 'Connects to Fyers WebSocket and streams live tick data for symbols in the database.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribed_symbols = []
    
    def get_symbols_from_django_orm(self):
        """Fetches the list of symbols using the Django ORM."""
        symbols_from_db = FundamentalsCompany.objects.values_list('symbol', flat=True)
        formatted_symbols = [f"NSE:{symbol}-EQ" for symbol in symbols_from_db]
        self.stdout.write(f"Fetched {len(formatted_symbols)} symbols from the database.")
        return formatted_symbols

    def handle(self, *args, **options):
        """The main logic of the command."""
        global fyers
        self.subscribed_symbols = self.get_symbols_from_django_orm()

        if not self.subscribed_symbols:
            self.stderr.write(self.style.ERROR("No symbols found. Exiting."))
            return

        client_id = load_file(CLIENT_ID_FILE)
        access_token = load_file(ACCESS_TOKEN_FILE)

        if not client_id:
            self.stderr.write(self.style.ERROR("Client ID not found."))
            return
        
        if not access_token:
            self.stdout.write("Access token not found, refreshing...")
            access_token = get_new_access_token_from_refresh()

        if not access_token:
            self.stderr.write(self.style.ERROR("Could not get access token. Exiting."))
            return

        fyers_access_token = f"{client_id}:{access_token}"

        # Define the callbacks inside handle or make them accessible
        def onmessage(message):
            self.stdout.write(self.style.SUCCESS(f"Response: {json.dumps(message, indent=2)}"))

        def onerror(message):
            self.stderr.write(self.style.ERROR(f"Error: {message}"))

        def onclose(message):
            self.stdout.write(self.style.WARNING(f"Connection closed: {message}"))

        def onopen():
            self.stdout.write(self.style.SUCCESS("WebSocket Connected!"))
            data_type = "SymbolUpdate"
            fyers.subscribe(symbols=self.subscribed_symbols, data_type=data_type)
            # The keep_running() is blocking, so we don't call it here.
            # The while loop below will keep the script alive.

        # Create a FyersDataSocket instance with the provided parameters
        fyers = data_ws.FyersDataSocket(
            access_token=fyers_access_token,
            log_path=os.path.join(os.getcwd(), "logs"),
            litemode=False,
            write_to_file=False,
            reconnect=True,
            on_connect=onopen,
            on_close=onclose,
            on_error=onerror,
            on_message=onmessage
        )

        # Establish a connection to the Fyers WebSocket
        fyers.connect()
        
        # Keep the main thread alive to listen for ticks
        self.stdout.write(self.style.SUCCESS("Listening for live ticks... Press Ctrl+C to exit."))
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Exiting..."))
            # The FyersDataSocket doesn't have an explicit close method in this interface,
            # letting the script exit should close the connection.


