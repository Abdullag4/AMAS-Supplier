import streamlit as st
import urllib.parse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

GOOGLE_CLIENT_ID = st.secrets["google"]["client_id"]
GOOGLE_CLIENT_SECRET = st.secrets["google"]["client_secret"]
REDIRECT_URI = st.secrets["google"]["redirect_uri"]  # e.g., "https://amas-supplier.streamlit.app/"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def get_google_oauth_flow():
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "project_id": "YOUR_PROJECT_ID",  # Replace with your actual GCP project ID
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
    A fallback sign-in approach that does NOT try to clear the code or rerun.

    1. If 'user_info' is already in session, return it (already signed in).
    2. Check if there's a 'code' in st.experimental_get_query_params() (we read it, but never remove it).
       - If we've not used it yet ('code_consumed' != True), attempt the token exchange.
       - On success, store user_info in session and set 'code_consumed = True'.
         That way, if user manually refreshes, we won't re-use that code again.
    3. If no code, show a "Sign in with Google" button.
    """
    # Already signed in?
    if "user_info" in st.session_state:
        return st.session_state["user_info"]

    # Parse code with the old "experimental" function (ignore the deprecation warning)
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        if not st.session_state.get("code_consumed", False):
            # Reconstruct the full authorization URL
            query_string = urllib.parse.urlencode(query_params, doseq=True)
            authorization_response = f"{REDIRECT_URI}?{query_string}"

            try:
                flow = get_google_oauth_flow()
                if "state" in query_params:
                    flow.state = query_params["state"][0]
                elif "state" in st.session_state:
                    flow.state = st.session_state["state"]

                # Exchange code for tokens
                flow.fetch_token(authorization_response=authorization_response)
                creds = flow.credentials

                # Verify the ID token
                request_session = google.auth.transport.requests.Request()
                id_info = id_token.verify_oauth2_token(
                    creds.id_token, request_session, GOOGLE_CLIENT_ID
                )

                user_email = id_info.get("email", "")
                user_name = id_info.get("name", "")
                if not user_name:
                    user_name = user_email.split("@")[0] or "Unnamed Supplier"

                # Store
                st.session_state["user_info"] = {"email": user_email, "name": user_name}
                st.session_state["code_consumed"] = True
                st.success(f"Signed in successfully as {user_name} ({user_email})!")

            except Exception as e:
                st.error(f"Sign-in error: {e}")
                return None

        # If code_consumed is already True, we do nothing; user_info might be set or might be None
        return st.session_state.get("user_info", None)

    else:
        # No code -> show sign-in button
        flow = get_google_oauth_flow()
        auth_url, state = flow.authorization_url(prompt="consent")
        st.session_state["state"] = state

        st.write("Click below to authorize with Google:")
        if st.button("Sign in with Google"):
            st.markdown(f"[Authorize with Google]({auth_url})")

        return None
