import streamlit as st
import json
import tempfile
from streamlit_google_auth import Authenticate

def create_temp_google_credentials():
    """
    Reads Google OAuth credentials from Streamlit secrets and writes them to a temporary JSON file.
    Returns the file path.
    """
    creds_json_str = st.secrets["google_oauth"]["json"]  # Get JSON string from secrets
    creds_dict = json.loads(creds_json_str)  # Convert JSON string to a dictionary

    # Write credentials to a temp file in text mode (`w` instead of `wb`)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as temp_file:
        json.dump(creds_dict, temp_file)  # Save JSON content
        temp_file.flush()  # Ensure data is written before passing the path
        return temp_file.name  # Return the temporary file path

def sign_in_with_google():
    """
    Handles Google Sign-In using streamlit-google-auth.
    Automatically persists session after authentication.
    """
    temp_creds_path = create_temp_google_credentials()  # Get temp credentials file path

    # Initialize authentication
    authenticator = Authenticate(
        secret_credentials_path=temp_creds_path,
        cookie_name="supplier_auth",
        cookie_key="this_is_secret_key",  # Use a strong key
        redirect_uri="https://amas-supplier.streamlit.app",
    )

    # Catch authentication event
    authenticator.check_authentification()

    # Show login button if user is not authenticated
    authenticator.login()

    # If user is authenticated, return their details
    if st.session_state.get("connected", False):
        user_info = {
            "email": st.session_state["user_info"].get("email"),
            "name": st.session_state["user_info"].get("name"),
        }
        return user_info
    return None
