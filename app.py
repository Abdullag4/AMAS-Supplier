import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier
from home import show_home_page  # Import the home page function

def main():
    # 1. Attempt to sign in with Google
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()  # Wait for sign-in

    # 2. Create or retrieve the supplier record
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])
    if not supplier:
        st.error("Could not retrieve or create a supplier record.")
        st.stop()

    # 3. Sidebar menu
    st.sidebar.title("Navigation")
    menu_choice = st.sidebar.radio("Go to:", ["Home", "Supplier Dashboard"])

    # 4. Show selected page
    if menu_choice == "Home":
        show_home_page()  # from home.py
    else:
        show_supplier_dashboard(supplier)

def show_supplier_dashboard(supplier):
    """
    Display the main supplier dashboard content.
    """
    st.title("AMAS Supplier App (OIDC)")
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")
    st.write("This is your supplier dashboard...")

    # Logout button
    if st.button("Log out"):
        st.logout()
        st.experimental_rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="AMAS Supplier App")
    main()
