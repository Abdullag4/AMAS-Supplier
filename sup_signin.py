import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

# ----------------------------------------------------------------------------
# Configuration / Secrets
# ----------------------------------------------------------------------------
GOOGLE_CLIENT_ID = st.secrets["google"]["client_id"]
GOOGLE_CLIENT_SECRET = st.secrets["google"]["client_secret"]
REDIRECT_URI = st.secrets["google"]["redirect_uri"]

# Use full scope URLs to match what Google returns.
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

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
                "redirect_uris": [REDIRECT_URI],
                "javascript_origins": [REDIRECT_URI.rstrip("/")]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

def sign_in_with_google():
    """
    Initiates the OAuth flow and returns user info after successful sign-in.
    
    The flow:
    1. If the user is already signed in (i.e. st.session_state has "user_info"), return it.
    2. Check if the URL contains an authorization code (using st.query_params).
       - If yes, exchange it for tokens, verify and store user info, clear the query, and rerun the app.
    3. If no code is present, display a sign-in button that takes the user to Google.
    """
    # If already signed in, return the stored user info.
    if "user_info" in st.session_state:
        return st.session_state["user_info"]

    # Use the new st.query_params API (instead of experimental_get_query_params)
    query_params = st.query_params
    flow = get_google_oauth_flow()

    if "code" in query_params:
        auth_code = query_params["code"][0]
        try:
            # Exchange the authorization code for tokens
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials

            # Verify the ID token to get user info
            request_session = google.auth.transport.requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, request_session, GOOGLE_CLIENT_ID
            )

            user_email = id_info.get("email")
            user_name = id_info.get("name", "")

            st.session_state["user_info"] = {"email": user_email, "name": user_name}
            st.success(f"Signed in successfully as {user_name} ({user_email})!")
            
            # Clear query parameters and rerun the app so that main content loads.
            st.experimental_set_query_params()
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            else:
                st.write("Please refresh the page to continue.")
                st.stop()

            return st.session_state["user_info"]

        except Exception as e:
            st.error(f"An error occurred during sign-in: {e}")
            return None

    # If no authorization code is present, display the sign-in prompt.
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.write("Click the button below to authorize with Google:")
    if st.button("Sign in with Google"):
        st.markdown(f"[Authorize with Google]({auth_url})")
    st.write("After authorizing, you will be redirected back with an authorization code.")

    return None
