import streamlit as st
from streamlit_google_auth import Authenticate

# Initialize authenticator
authenticator = Authenticate(
    secret_credentials_path="google_credentials.json",  # Path to your Google credentials JSON
    cookie_name="supplier_auth",  # Name of the authentication cookie
    cookie_key="my_secret_key",  # Change this to a strong secret key
    redirect_uri="https://amas-supplier.streamlit.app/",  # Your app's deployed URL
)

def sign_in_with_google():
    """
    Handles Google Sign-In using streamlit-google-auth.
    Automatically persists session after authentication.
    """
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
