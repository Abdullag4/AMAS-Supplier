import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier

def main():
    st.title("AMAS Supplier App")
    
    # Step 1: Trigger the Google sign-in flow.
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()  # Halt execution until sign-in completes or fails.
    
    # Step 2: Attempt to retrieve (or create) a supplier record in the Neon database.
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])
    
    # Debug print to see what `supplier` returned.
    st.write("DEBUG => Supplier object:", supplier)
    
    # Step 3: If supplier is None, display an error and stop to avoid subscript errors.
    if not supplier:
        st.error("Could not retrieve or create a supplier record. Please check the logs or contact support.")
        st.stop()
    
    # Step 4: Supplier is valid; display a welcome message and supplier details.
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")
    st.write("This is your supplier dashboard. [Add your app content here...]")

if __name__ == "__main__":
    main()
