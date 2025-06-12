# from django.shortcuts import render, redirect
# from .forms import FyersLoginForm
# from .login import generate_auth_url, get_access_token  # Helper functions for Fyers API
# from django.contrib import messages


# ##########################################################################################
# ####                           LOGIN START                                             ###
# ##########################################################################################

# # Redirect URL registered with Fyers
# REDIRECT_URL = "http://127.0.0.1:8000/callback/"

# def fyers_login_view(request):
#     """
#     Render the login form and redirect to the Fyers authorization URL.
#     """
#     if request.method == "POST":
#         form = FyersLoginForm(request.POST)
#         if form.is_valid():
#             client_id = form.cleaned_data['client_id']
#             secret_key = form.cleaned_data['secret_key']

#             # Save the client_id and secret_key in the session for use in callback
#             request.session['client_id'] = client_id
#             request.session['secret_key'] = secret_key

#             # Generate the Fyers authorization URL with a state parameter
#             state = "some_unique_state_value"  # Replace or generate dynamically
#             auth_url = generate_auth_url(client_id, REDIRECT_URL, state)
#             return redirect(auth_url)  # Redirect the user to the authorization URL
#     else:
#         form = FyersLoginForm()

#     return render(request, 'login.html', {'form': form})

# def fyers_callback(request):
#     """
#     Handle the callback from Fyers with the authorization code.
#     """
#     # Extract the full query string
#     from urllib.parse import parse_qs, urlparse

#     full_url = request.get_full_path()
#     query_params = parse_qs(urlparse(full_url).query)
#     auth_code = query_params.get("auth_code", [None])[0]  # Get the first value of auth_code

#     if not auth_code:
#         messages.error(request, "Authorization code missing.")
#         return redirect('fyers_login')

#     # Retrieve client_id and secret_key from session
#     client_id = request.session.get('client_id')
#     secret_key = request.session.get('secret_key')

#     if not client_id or not secret_key:
#         messages.error(request, "Session expired. Please log in again.")
#         return redirect('fyers_login')

#     try:
#         # Exchange the authorization code for an access token
#         token_response = get_access_token(client_id, secret_key, auth_code, REDIRECT_URL)
#         access_token = token_response.get("access_token")

#         if access_token:
#             messages.success(request, "Login successful!")
#             return redirect('/dashboard/')  # Redirect to the admin page after successful login
#         else:
#             error_message = token_response.get("message", "Unknown error")
#             messages.error(request, f"Login failed: {error_message}")
#             return redirect('fyers_login')
#     except ValueError as e:
#         messages.error(request, str(e))
#         return redirect('fyers_login')


import time
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import FyersLoginForm
from .login import generate_auth_url, get_access_token
from urllib.parse import parse_qs, urlparse

# Redirect URL registered with Fyers
REDIRECT_URL = "http://127.0.0.1:8000/callback/"

def fyers_login_view(request):
    """
    Renders the login form and redirects the user to the Fyers authorization URL upon submission.
    """
    if request.method == "POST":
        form = FyersLoginForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data['client_id']
            secret_key = form.cleaned_data['secret_key']

            # Store credentials in the session for the callback to use.
            request.session['client_id'] = client_id
            request.session['secret_key'] = secret_key
            
            # Generate the auth URL and redirect the user.
            state = "some_unique_state_value"
            auth_url = generate_auth_url(client_id, REDIRECT_URL, state)
            return redirect(auth_url)
    else:
        form = FyersLoginForm()

    return render(request, 'login.html', {'form': form})

def fyers_callback(request):
    """
    Handles the callback from Fyers after the user authorizes the app.
    Exchanges the auth code for an access token and redirects to the dashboard.
    """
    query_params = parse_qs(urlparse(request.get_full_path()).query)
    auth_code = query_params.get("auth_code", [None])[0]

    if not auth_code:
        messages.error(request, "Authorization failed: No authorization code received from Fyers.")
        return redirect('fyers_login')

    client_id = request.session.get('client_id')
    secret_key = request.session.get('secret_key')

    if not client_id or not secret_key:
        messages.error(request, "Your session has expired. Please try logging in again.")
        return redirect('fyers_login')

    try:
        # --- FIX: Added the missing REDIRECT_URL argument back into the function call ---
        token_response = get_access_token(client_id, secret_key, auth_code, REDIRECT_URL)
        access_token = token_response.get("access_token")

        if access_token:
            request.session['fyers_access_token'] = access_token
            request.session['fyers_access_time'] = time.time()
            
            messages.success(request, "Login Successful!")
            
            return redirect(reverse('dashboard:home'))
        else:
            error_message = token_response.get("message", "An unknown error occurred during authentication.")
            messages.error(request, f"Login Failed: {error_message}")
            return redirect('fyers_login')

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")
        return redirect('fyers_login')

def fyers_logout_view(request):
    """
    Logs the user out by clearing the entire session.
    """
    request.session.flush() # Clears all data from the session
    messages.info(request, "You have been successfully logged out.")
    return redirect(reverse('fyers_login'))