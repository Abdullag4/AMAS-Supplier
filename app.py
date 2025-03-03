import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier
from streamlit_js_eval import get_cookie

def main():
    st.title("AMAS Supplier App")

    # 1️⃣ Check if user is stored in cookies
    saved_email = get_cookie("user_email")
    saved_name = get_cookie("user_name")

    if saved_email and saved_name:
        user_info = {"email": saved_email, "name": saved_name}
        st.session_state["user_info"] = user_info
    else:
        user_info = sign_in_with_google()

    if not user_info:
        st.stop()

    # 2️⃣ Create or retrieve supplier record
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])
    
    st.write("DEBUG => Supplier object:", supplier)
    if not supplier:
        st.error("Could not retrieve or create a supplier record.")
        st.stop()

    # 3️⃣ Display supplier dashboard
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")
    st.write("This is your supplier dashboard...")

if __name__ == "__main__":
    main()
