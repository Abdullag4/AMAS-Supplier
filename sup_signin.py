import streamlit as st
from streamlit_google_auth import Authenticate
import tempfile
import json

def create_temp_creds_file():
    """
    Retrieves the JSON credentials from st.secrets
    and writes them to a temporary file, returning the file path.
    """
    creds_json_str = st.secrets["google_oauth"]["json"]  # The multiline JSON string
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(creds_json_str.encode("utf-8"))
        tmp.flush()
        return tmp.name

def sign_in_with_google():
    # 1. Create temp file with your Google OAuth credentials
    temp_creds_path = create_temp_creds_file()

    # 2. Initialize the authenticator using that file
    authenticator = Authenticate(
        secret_credentials_path=temp_creds_path,
        cookie_name="supplier_auth",
        cookie_key="some_random_secret_key",  # set a strong key here
        redirect_uri="https://amas-supplier.streamlit.app",
    )

    # 3. Catch authentication event
    authenticator.check_authentification()

    # 4. Show login button if user is not authenticated
    authenticator.login()

    # 5. If user is authenticated, return their info
    if st.session_state.get("connected"):
        user_info = {
            "email": st.session_state["user_info"].get("email"),
            "name": st.session_state["user_info"].get("name"),
        }
        return user_info
    return None
