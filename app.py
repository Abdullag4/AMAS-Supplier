import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier

def main():
    st.title("AMAS Supplier App")

    user_info = sign_in_with_google()
    if not user_info:
        st.stop()  # Wait for sign-in to complete.

    supplier = get_or_create_supplier(user_info["name"], user_info["email"])
    
    st.write("DEBUG => Supplier object:", supplier)
    if not supplier:
        st.error("Could not retrieve or create a supplier record.")
        st.stop()

    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")
    st.write("This is your supplier dashboard...")

if __name__ == "__main__":
    main()
