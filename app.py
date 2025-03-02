import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier

def main():
    st.title("AMAS Supplier App")

    # 1. Google Sign-In
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()  # Wait for sign-in

    # 2. Create or retrieve the supplier record
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])

    st.write("DEBUG => Supplier object:", supplier)

    if not supplier:
        st.error("Could not retrieve or create a supplier record. Please check logs.")
        st.stop()

    # 3. Display the dashboard
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")
    st.write("This is your supplier dashboard. [Add your content here...]")

if __name__ == "__main__":
    main()
