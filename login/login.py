from fyers_apiv3 import fyersModel  # Ensure this library is installed in your environment

ACCESS_TOKEN_FILE = r"credentials\access_token.txt"  # File to save the access token
REFRESH_TOKEN_FILE = r"credentials\refresh_token.txt"  # File to save the refresh token
client_id = r"credentials\client_id.txt"

def generate_auth_url(client_id, redirect_url, state="default_state"):
    """
    Generate the Fyers OAuth authorization URL with a valid state.
    """
    auth_url = (
        f"https://api-t1.fyers.in/api/v3/generate-authcode?client_id={client_id}&redirect_uri={redirect_url}"
        f"&response_type=code&state={state}"
         
    )
    return auth_url

def get_access_token(client_id, secret_key, auth_code, redirect_url):
    """
    Generate the access token using the Fyers API session model and save it to a text file.
    Also saves the refresh token to refresh_token.txt if available.
    """
    # Create a session object
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_url,
        response_type="code",
        grant_type="authorization_code"
    )

    # Set the authorization code in the session object
    session.set_token(auth_code)

    # Generate the access token
    response = session.generate_token()
    print("Access Token Response:", response)  # Debugging: Print the response

    # Check if the response contains the access token
    if "access_token" in response:
        # Save the access token to a text file
        save_access_token(response["access_token"])
        print(f"Access token saved to {ACCESS_TOKEN_FILE}")
        # Save the refresh token if available
        if "refresh_token" in response:
            save_refresh_token(response["refresh_token"])
            print(f"Refresh token saved to {REFRESH_TOKEN_FILE}")
        return response
    else:
        raise ValueError(f"Error fetching access token: {response}")

def save_access_token(access_token):
    """
    Save the access token to a text file, overwriting any existing token.
    """
    with open(ACCESS_TOKEN_FILE, "w") as file:
        file.write(access_token)
    print(f"Access token saved to {ACCESS_TOKEN_FILE}")

def save_refresh_token(refresh_token):
    """
    Save the refresh token to a text file, overwriting any existing token.
    """
    with open(REFRESH_TOKEN_FILE, "w") as file:
        file.write(refresh_token)
    print(f"Refresh token saved to {REFRESH_TOKEN_FILE}")
