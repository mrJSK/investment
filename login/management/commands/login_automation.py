import base64
import os
import json
import requests
import pyotp  # For TOTP generation
from fyers_apiv3 import fyersModel
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# File paths for credentials and ChromeDriver
ACCESS_TOKEN_PATH = r"credentials\access_token.txt"
CLIENT_ID_PATH = r"credentials\client_id.txt"
CHROME_DRIVER_PATH = r"C:\chrome-headless\chrome-headless-shell.exe"
SECRET_KEY_PATH = r"credentials\secret_key.txt"
PASS_KEY = r"credentials\passkey.txt"

def load_secret_key():
    """
    Load the secret key from the text file.
    """
    if os.path.exists(SECRET_KEY_PATH):
        with open(SECRET_KEY_PATH, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError(f"Secret key file '{SECRET_KEY_PATH}' not found.")

def load_access_token():
    """
    Load the access token from the text file.
    """
    if os.path.exists(ACCESS_TOKEN_PATH):
        with open(ACCESS_TOKEN_PATH, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError(f"Access token file '{ACCESS_TOKEN_PATH}' not found.")

def load_client_id():
    """
    Load the client ID from the text file.
    """
    if os.path.exists(CLIENT_ID_PATH):
        with open(CLIENT_ID_PATH, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError(f"Client ID file '{CLIENT_ID_PATH}' not found.")

def load_passkey():
    """
    Load the passkey from the text file.
    """
    if os.path.exists(PASS_KEY):
        with open(PASS_KEY, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError(f"Passkey file '{PASS_KEY}' not found.")
        
        
class Command(BaseCommand):
    help = "Automates Fyers login and token generation."

    def handle(self, *args, **kwargs):
        CLIENT_ID = load_client_id()  # Add your client_id here
        SECRET_KEY = load_secret_key()  # Add your secret_key here
        REDIRECT_URL = "https://trade.fyers.in/api-login/redirect-uri/index.html"  # Update to your redirect URL

        raw_secret = load_secret_key()
        base32_secret = base64.b32encode(raw_secret.encode()).decode()

        TOTP_SECRET = base32_secret  # Add your TOTP secret here
        PIN = load_passkey()  # Add your Fyers PIN here

        try:
            self.stdout.write("Launching headless browser to log in...")

            # Generate TOTP dynamically
            totp = pyotp.TOTP(TOTP_SECRET)
            current_totp = totp.now()

            # Start a headless browser session
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")  # Optional: Useful for Docker

            driver_path = CHROME_DRIVER_PATH  # Update with the path to your ChromeDriver
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)

            try:
                # Visit the auth URL
                session = fyersModel.SessionModel(
                    client_id=CLIENT_ID,
                    secret_key=SECRET_KEY,
                    redirect_uri=REDIRECT_URL,
                    response_type="code"
                )
                auth_url = session.generate_authcode()
                driver.get(auth_url)

                # Step 1: Input mobile number
                driver.implicitly_wait(5)  # Wait for the page to load
                mobile_input = driver.find_element(By.ID, "fy_client_id")
                mobile_input.send_keys(load_client_id())
                login_button = driver.find_element(By.ID, "clientIdSubmit")
                login_button.click()

                # Step 2: Enter TOTP
                driver.implicitly_wait(5)  # Wait for OTP input fields to load
                otp_ids = ["first", "second", "third", "fourth", "fifth", "sixth"]
                for i, digit in enumerate(current_totp):
                    otp_input = driver.find_element(By.ID, otp_ids[i])
                    otp_input.send_keys(digit)
                otp_submit_button = driver.find_element(By.ID, "confirmOtpSubmit")
                otp_submit_button.click()

                # Step 3: Enter PIN
                driver.implicitly_wait(5)  # Wait for PIN input fields to load
                pin_ids = ["first", "second", "third", "fourth"]
                for i, digit in enumerate(PIN):
                    pin_input = driver.find_element(By.ID, pin_ids[i])
                    pin_input.send_keys(digit)
                pin_submit_button = driver.find_element(By.ID, "verifyPinSubmit")
                pin_submit_button.click()

                # Step 4: Capture auth_code from redirect URL
                driver.implicitly_wait(5)
                current_url = driver.current_url
                from urllib.parse import urlparse, parse_qs
                query_params = parse_qs(urlparse(current_url).query)
                auth_code = query_params.get("auth_code", [None])[0]

                if not auth_code:
                    self.stderr.write("Failed to retrieve authorization code.")
                    return

                self.stdout.write("Exchanging auth code for access token...")

                # Generate access token
                session.set_token(auth_code)
                token_response = session.generate_token()

                if token_response and token_response.get('s') == 'ok':
                    self.stdout.write("Access token generated successfully!")

                    access_token = token_response['access_token']

                    # Save access token to access_token.txt
                    self.save_access_token(access_token)

                    self.stdout.write("Token saved successfully.")
                else:
                    self.stderr.write(f"Failed to generate token: {token_response.get('message', 'Unknown error')}")

            finally:
                driver.quit()

        except Exception as e:
            self.stderr.write(f"Error: {str(e)}")

    @staticmethod
    def save_access_token(access_token):
        """
        Save the access token to a text file, overwriting any existing token.
        """
        with open(ACCESS_TOKEN_PATH, "w") as file:
            file.write(access_token)
        print(f"Access token saved to {ACCESS_TOKEN_PATH}")
