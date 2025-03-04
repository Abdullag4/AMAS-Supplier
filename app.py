import streamlit as st
from sup_signin import sign_in_with_google
# Example DB function if you want to store the user
from supplier_db import get_or_create_supplier

def main():
    st.title("AMAS Supplier App (OIDC)")

    # 1. Attempt to sign in with Google
    user_info = sign_in_with_google()  # This blocks until the user is logged in

    # 2. If you have a DB function, retrieve or create the supplier record
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])
    if not supplier:
        st.error("Could not retrieve or create supplier record.")
        st.stop()

    # 3. Display a welcome message
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")

    # 4. Logout button
    if st.button("Log out"):
        st.logout()  # Removes the identity cookie
        st.experimental_rerun()

if __name__ == "__main__":
    main()
