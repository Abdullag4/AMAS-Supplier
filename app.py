import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import (
    get_or_create_supplier,
    save_supplier_details,
    get_missing_fields,
    get_supplier_form_structure
)
from home import show_home_page

def main():
    st.title("AMAS Supplier App")

    # 1. Sign in with Google
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()

    # 2. Get supplier record
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])

    # 3. Check if supplier needs to complete registration
    missing_fields = get_missing_fields(supplier)
    if missing_fields:
        show_supplier_registration_form(supplier, missing_fields)
        st.stop()

    # 4. Sidebar Navigation
    st.sidebar.title("Navigation")
    menu_choice = st.sidebar.radio("Go to:", ["Home", "Supplier Dashboard"])

    # 5. Show the selected page
    if menu_choice == "Home":
        show_home_page()
    else:
        show_supplier_dashboard(supplier)

def show_supplier_registration_form(supplier, missing_fields):
    """Displays a form for new suppliers to complete their registration."""
    st.warning("Please complete your supplier profile before continuing.")

    # Get form structure
    form_structure = get_supplier_form_structure()

    # Initialize form_data with existing values
    form_data = {field: supplier.get(field, "") for field in form_structure.keys()}

    # Display inputs only for missing fields
    for field in missing_fields:
        field_config = form_structure[field]
        label = field_config["label"]
        field_type = field_config["type"]

        if field_type == "text":
            form_data[field] = st.text_input(label, form_data[field])
        elif field_type == "select":
            form_data[field] = st.selectbox(label, field_config["options"])
        elif field_type == "textarea":
            form_data[field] = st.text_area(label, form_data[field])

    if st.button("Submit"):
        save_supplier_details(supplier["supplierid"], form_data)
        st.success("Profile updated successfully! Redirecting to the dashboard...")
        st.rerun()  # 🔥 Fix: Replaces `st.experimental_rerun()`

def show_supplier_dashboard(supplier):
    """Displays the supplier dashboard."""
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")

    # Logout button
    if st.button("Log out"):
        st.logout()
        st.rerun()  # 🔥 Fix: Replaces `st.experimental_rerun()`

if __name__ == "__main__":
    main()
