import os
import streamlit as st
import requests
import json

# Google-specific libraries for OAuth
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

# ----------------------------------------------------------------------------
# Configuration / Secrets
# ----------------------------------------------------------------------------
# For security, store these in Streamlit secrets or environment variables.
# Example usage: st.secrets["google_client_id"]
# Or: os.environ.get("GOOGLE_CLIENT_ID")
# Make sure to configure your Google Cloud OAuth Consent Screen & credentials.

GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# The SCOPES you need for basic profile info (email, name, etc.).
# Adjust if you need other OAuth scopes, e.g., to read Google Drive, etc.
SCOPES = ["openid", "email", "profile"]

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------

def get_google_oauth_flow():
    """
    Creates and configures the Google OAuth Flow object.
    """
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "project_id": "YOUR_PROJECT_ID",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [
                    # For local development, match the URL used by your app
                    "http://localhost:8501"
                ],
                "javascript_origins": [
                    "http://localhost:8501"
                ]
            }
        },
        scopes=SCOPES,
        redirect_uri="http://localhost:8501"
    )

def sign_in_with_google():
    """
    Initiates the OAuth flow and returns user info after successful sign-in.

    NOTE: In a typical web app, you'd have a separate callback route. 
    In Streamlit, you can handle it in-app, but you need to manage 
    the redirection carefully. This function is a simplified approach.
    """
    flow = get_google_oauth_flow()

    # Get authorization URL from the flow
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.write("Click the button below to authorize with Google:")
    if st.button("Sign in with Google"):
        # In a normal web app, you'd redirect the user to auth_url
        # For demonstration, open in new tab (not fully automatic):
        st.markdown(f"[Authorize with Google]({auth_url})")

    st.write("**After you authorize, you’ll get a code from Google**. " 
             "Paste it below to complete sign-in:")

    auth_code = st.text_input("Enter the authorization code here:")
    if auth_code:
        try:
            # Exchange authorization code for a token
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials

            # Use the ID token to get user info
            request_session = google.auth.transport.requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, request_session, GOOGLE_CLIENT_ID
            )

            # Extract relevant profile info
            user_email = id_info.get("email")
            user_name = id_info.get("name", "")
            # Or id_info["picture"] for user avatar, etc.

            st.success(f"Signed in successfully as {user_name} ({user_email})!")

            return {
                "email": user_email,
                "name": user_name,
            }
        except Exception as e:
            st.error(f"An error occurred during sign-in: {e}")

    return None

