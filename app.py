import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier

def main():
    st.title("AMAS Supplier App")

    # Sign-in with Google
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()

    # Retrieve or create supplier record
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])

    st.write("DEBUG => Supplier object:", supplier)
    if not supplier:
        st.error("Could not retrieve or create a supplier record.")
        st.stop()

    # Display supplier dashboard
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")
    st.write("This is your supplier dashboard...")

    # Logout button
    if st.button("Log out"):
        from streamlit_google_auth import Authenticate
        authenticator = Authenticate(
            secret_credentials_path="google_credentials.json",
            cookie_name="supplier_auth",
            cookie_key="my_secret_key",
            redirect_uri="https://amas-supplier.streamlit.app/",
        )
        authenticator.logout()
        st.rerun()

if __name__ == "__main__":
    main()
