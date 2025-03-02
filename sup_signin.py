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
# Access your Google OAuth credentials from the 'google' section in Streamlit secrets.
GOOGLE_CLIENT_ID = st.secrets["google"]["client_id"]
GOOGLE_CLIENT_SECRET = st.secrets["google"]["client_secret"]
REDIRECT_URI = st.secrets["google"]["redirect_uri"]

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Scopes required for basic profile info (email, name, etc.)
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
                "project_id": "YOUR_PROJECT_ID",  # Replace with your actual project id
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [
                    REDIRECT_URI  # Use the production redirect URI from secrets
                ],
                # For javascript origins, remove any trailing slash
                "javascript_origins": [
                    REDIRECT_URI.rstrip("/")
                ]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

def sign_in_with_google():
    """
    Initiates the OAuth flow and returns user info after successful sign-in.

    This version automatically checks for the authorization code in the URL
    query parameters (using st.experimental_get_query_params) so that the user
    doesn't have to manually copy-paste it.
    """
    flow = get_google_oauth_flow()

    # Check if an authorization code is present in the URL
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        auth_code = query_params["code"][0]
        try:
            # Exchange the authorization code for a token
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials

            # Verify the ID token to get user info
            request_session = google.auth.transport.requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, request_session, GOOGLE_CLIENT_ID
            )

            # Extract relevant profile information
            user_email = id_info.get("email")
            user_name = id_info.get("name", "")
            st.success(f"Signed in successfully as {user_name} ({user_email})!")
            return {
                "email": user_email,
                "name": user_name,
            }
        except Exception as e:
            st.error(f"An error occurred during sign-in: {e}")
            return None

    # If no code is found, display the sign-in prompt
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.write("Click the button below to authorize with Google:")
    if st.button("Sign in with Google"):
        st.markdown(f"[Authorize with Google]({auth_url})")

    st.write("After authorizing, you will be redirected back with an authorization code.")

    return None
