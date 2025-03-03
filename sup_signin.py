import streamlit as st
import urllib.parse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
from streamlit_js_eval import get_cookie, set_cookie

GOOGLE_CLIENT_ID = st.secrets["google"]["client_id"]
GOOGLE_CLIENT_SECRET = st.secrets["google"]["client_secret"]
REDIRECT_URI = st.secrets["google"]["redirect_uri"]

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
                "project_id": "YOUR_PROJECT_ID",
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
    1. If 'user_info' exists in cookies, use it (persistent login).
    2. Otherwise, if 'code' is in URL, exchange it for a token and save user_info in a cookie.
    3. If neither, show Google sign-in button.
    """
    # 1️⃣ Check if user info exists in cookies (persistent login)
    saved_email = get_cookie("user_email")
    saved_name = get_cookie("user_name")
    
    if saved_email and saved_name:
        st.session_state["user_info"] = {"email": saved_email, "name": saved_name}
        return st.session_state["user_info"]

    # 2️⃣ Parse Google OAuth response
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        if not st.session_state.get("code_consumed", False):
            query_string = urllib.parse.urlencode(query_params, doseq=True)
            authorization_response = f"{REDIRECT_URI}?{query_string}"

            try:
                flow = get_google_oauth_flow()
                if "state" in query_params:
                    flow.state = query_params["state"][0]
                elif "state" in st.session_state:
                    flow.state = st.session_state["state"]

                # Exchange the authorization code for an access token
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

                # 3️⃣ Store user info in session and cookies
                st.session_state["user_info"] = {"email": user_email, "name": user_name}
                set_cookie("user_email", user_email)
                set_cookie("user_name", user_name)

                st.session_state["code_consumed"] = True
                st.success(f"Signed in successfully as {user_name} ({user_email})!")

            except Exception as e:
                st.error(f"Sign-in error: {e}")
                return None

        return st.session_state.get("user_info", None)

    # 4️⃣ No session or cookie -> show Google sign-in button
    flow = get_google_oauth_flow()
    auth_url, state = flow.authorization_url(prompt="consent")
    st.session_state["state"] = state

    st.write("Click below to authorize with Google:")
    if st.button("Sign in with Google"):
        st.markdown(f"[Authorize with Google]({auth_url})")

    return None
