import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier
from streamlit_google_auth import Authenticate

def main():
    st.title("AMAS Supplier App")

    user_info = sign_in_with_google()
    if not user_info:
        st.stop()

    supplier = get_or_create_supplier(user_info["name"], user_info["email"])
    if not supplier:
        st.error("Could not retrieve or create a supplier record.")
        st.stop()

    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")

    # Logout button
    if st.button("Log out"):
        authenticator = Authenticate(
            secret_credentials_path="",  # Not needed for logout
            cookie_name="supplier_auth",
            cookie_key="this_is_secret_key",
            redirect_uri="https://amas-supplier.streamlit.app/",
        )
        authenticator.logout()
        st.experimental_rerun()

if __name__ == "__main__":
    main()
