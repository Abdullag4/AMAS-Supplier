import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier

def main():
    st.title("AMAS Supplier App")
    
    # Trigger the Google sign-in flow.
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()  # Halt execution until sign-in is complete.
    
    # Retrieve (or create) the supplier record in your Neon database.
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])
    
    # Display a welcome message and supplier details.
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")
    st.write("This is your supplier dashboard. [Add your app content here...]")

if __name__ == "__main__":
    main()
