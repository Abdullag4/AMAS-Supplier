import streamlit as st
import urllib.parse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

GOOGLE_CLIENT_ID = st.secrets["google"]["client_id"]
GOOGLE_CLIENT_SECRET = st.secrets["google"]["client_secret"]
REDIRECT_URI = st.secrets["google"]["redirect_uri"]  # e.g. "https://amas-supplier.streamlit.app/"

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
    Google Sign-In flow using old 'experimental' query parameter functions,
    since your environment doesn't actually support the new st.set_query_params().
    """
    # 1. Check if user already in session
    if "user_info" in st.session_state:
        return st.session_state["user_info"]

    # 2. Read query params using the experimental function
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        # Prevent reusing the code
        if st.session_state.get("code_consumed", False):
            return st.session_state.get("user_info", None)

        # Reconstruct the full redirect URL
        query_string = urllib.parse.urlencode(query_params, doseq=True)
        authorization_response = f"{REDIRECT_URI}?{query_string}"

        try:
            flow = get_google_oauth_flow()
            if "state" in query_params:
                flow.state = query_params["state"][0]
            elif "state" in st.session_state:
                flow.state = st.session_state["state"]

            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials

            # Verify ID token
            request_session = google.auth.transport.requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, request_session, GOOGLE_CLIENT_ID
            )

            user_email = id_info.get("email", "")
            user_name = id_info.get("name", "")
            if not user_name:
                user_name = user_email.split("@")[0] or "Unnamed Supplier"

            st.session_state["user_info"] = {"email": user_email, "name": user_name}
            st.session_state["code_consumed"] = True
            st.success(f"Signed in successfully as {user_name} ({user_email})!")

            # Clear query parameters using experimental_set_query_params
            st.experimental_set_query_params()
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            else:
                st.warning("Please refresh manually to continue.")
                st.stop()

            return st.session_state["user_info"]

        except Exception as e:
            st.error(f"An error occurred during sign-in: {e}")
            return None

    else:
        # 3. No code present -> show button
        flow = get_google_oauth_flow()
        auth_url, state = flow.authorization_url(prompt="consent")
        st.session_state["state"] = state

        st.write("Click below to authorize with Google:")
        if st.button("Sign in with Google"):
            st.markdown(f"[Authorize with Google]({auth_url})")

        return None
