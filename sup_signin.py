import streamlit as st
import urllib.parse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

GOOGLE_CLIENT_ID = st.secrets["google"]["client_id"]
GOOGLE_CLIENT_SECRET = st.secrets["google"]["client_secret"]
REDIRECT_URI = st.secrets["google"]["redirect_uri"]
# e.g., "https://amas-supplier.streamlit.app/"

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
                "project_id": "YOUR_PROJECT_ID",  # Replace with your actual project name/ID
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
    Fallback sign-in approach for older Streamlit versions.
    
    Flow:
      1. If st.session_state has "user_info", return it (already signed in).
      2. Parse the authorization code manually from st.experimental_get_query_params()
         and do NOT attempt to remove or rewrite the URL afterward.
      3. If code is found and hasn't been "consumed," exchange it for tokens.
         - On success, store user info in session_state, mark code as consumed,
           and display a link back to your root app URL (without the code).
      4. If no code is present, show a "Sign in with Google" button.
    """
    # 1. Check if user_info is already in session state
    if "user_info" in st.session_state:
        return st.session_state["user_info"]

    # 2. Parse code manually from old experimental function
    query_params = {}
    if hasattr(st, "experimental_get_query_params"):
        query_params = st.experimental_get_query_params()
    # If your Streamlit is so old it lacks even that, you'd have to parse os.environ or request headers manually.

    if "code" in query_params:
        # Avoid re-using a one-time code
        if st.session_state.get("code_consumed", False):
            return st.session_state.get("user_info", None)

        # Reconstruct the full "authorization_response" URL
        query_string = urllib.parse.urlencode(query_params, doseq=True)
        authorization_response = f"{REDIRECT_URI}?{query_string}"

        try:
            flow = get_google_oauth_flow()

            # State handling
            if "state" in query_params:
                flow.state = query_params["state"][0]
            elif "state" in st.session_state:
                flow.state = st.session_state["state"]

            # Exchange code
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials

            # Verify ID token
            req_session = google.auth.transport.requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, req_session, GOOGLE_CLIENT_ID
            )

            user_email = id_info.get("email")
            user_name = id_info.get("name", "")
            st.session_state["user_info"] = {"email": user_email, "name": user_name}
            st.success(f"Signed in successfully as {user_name} ({user_email})!")
            st.session_state["code_consumed"] = True

            # 3. Show a link or button to your app's root URL
            #    so user can proceed without that code in the URL
            st.info("Click below to continue without the code in the URL.")
            app_root_link = REDIRECT_URI  # e.g. "https://amas-supplier.streamlit.app/"
            st.markdown(f"[Continue to App]({app_root_link})")

            return st.session_state["user_info"]

        except Exception as e:
            st.error(f"Error during sign-in: {e}")
            return None

    else:
        # 4. No code present, show sign-in button
        flow = get_google_oauth_flow()
        auth_url, state = flow.authorization_url(prompt="consent")
        st.session_state["state"] = state

        st.write("Click below to authorize with Google:")
        if st.button("Sign in with Google"):
            st.markdown(f"[Authorize with Google]({auth_url})")
        st.write("After authorizing, you'll return here with a code.")
        return None
