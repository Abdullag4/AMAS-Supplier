import streamlit as st
import urllib.parse
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
    
    Flow:
      1. If the user is already signed in (stored in session state), return that info.
      2. Check if the URL contains an authorization code (using st.query_params).
         - Process it only if it hasn't been consumed yet.
         - Reconstruct the full authorization response URL and exchange it for tokens.
         - Store the user info, mark the code as consumed, clear query params, and rerun.
      3. If no code is present, display a sign-in button that sends the user to Google.
    """
    # Return if already signed in.
    if "user_info" in st.session_state:
        return st.session_state["user_info"]

    query_params = st.query_params

    if "code" in query_params:
        # Check if we've already processed this code.
        if st.session_state.get("code_consumed", False):
            return st.session_state.get("user_info", None)
        
        # Reconstruct the full authorization response URL.
        query_string = urllib.parse.urlencode(query_params, doseq=True)
        authorization_response = f"{REDIRECT_URI}?{query_string}"
        
        try:
            flow = get_google_oauth_flow()
            # Use the state from query parameters if available.
            if "state" in query_params:
                flow.state = query_params["state"][0]
            elif "state" in st.session_state:
                flow.state = st.session_state["state"]
            
            # Pass the full URL to fetch_token.
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials

            # Verify the ID token to get user info.
            request_session = google.auth.transport.requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, request_session, GOOGLE_CLIENT_ID
            )

            user_email = id_info.get("email")
            user_name = id_info.get("name", "")

            st.session_state["user_info"] = {"email": user_email, "name": user_name}
            st.success(f"Signed in successfully as {user_name} ({user_email})!")
            st.session_state["code_consumed"] = True

            # Clear the query parameters and rerun the app.
            st.experimental_set_query_params({})
            st.experimental_rerun()
            return st.session_state["user_info"]

        except Exception as e:
            st.error(f"An error occurred during sign-in: {e}")
            return None

    else:
        # No authorization code present; generate the auth URL.
        flow = get_google_oauth_flow()
        auth_url, state = flow.authorization_url(prompt="consent")
        st.session_state["state"] = state

        st.write("Click the button below to authorize with Google:")
        if st.button("Sign in with Google"):
            st.markdown(f"[Authorize with Google]({auth_url})")
        st.write("After authorizing, you'll be redirected back with an authorization code.")

    return None
