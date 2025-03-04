import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier, update_supplier
from home import show_home_page

def main():
    st.title("AMAS Supplier App")

    # 1. Sign in with Google
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()

    # 2. Check if supplier exists, create if not
    supplier = get_or_create_supplier(user_info["name"], user_info["email"])

    # 3. Check if the supplier is missing important data
    if supplier_needs_update(supplier):
        show_supplier_registration_form(supplier)
        st.stop()  # Prevent access to dashboard until form is completed

    # 4. Sidebar Navigation
    st.sidebar.title("Navigation")
    menu_choice = st.sidebar.radio("Go to:", ["Home", "Supplier Dashboard"])

    # 5. Show the selected page
    if menu_choice == "Home":
        show_home_page()
    else:
        show_supplier_dashboard(supplier)

def supplier_needs_update(supplier):
    """
    Check if the supplier has missing required fields.
    Example: If supplier type, country, and contact phone are empty, return True.
    """
    required_fields = ["suppliertype", "country", "contactphone"]
    return any(not supplier[field] for field in required_fields)

def show_supplier_registration_form(supplier):
    """Displays a form for new suppliers to complete their registration."""
    st.warning("Please complete your supplier profile before continuing.")
    
    # Form inputs
    supplier_type = st.selectbox("Supplier Type", ["Manufacturer", "Distributor", "Retailer", "Other"])
    country = st.text_input("Country", supplier.get("country", ""))
    city = st.text_input("City", supplier.get("city", ""))
    address = st.text_input("Address", supplier.get("address", ""))
    postal_code = st.text_input("Postal Code", supplier.get("postalcode", ""))
    contact_name = st.text_input("Contact Name", supplier.get("contactname", ""))
    contact_phone = st.text_input("Contact Phone", supplier.get("contactphone", ""))
    payment_terms = st.text_area("Payment Terms", supplier.get("paymentterms", ""))
    bank_details = st.text_area("Bank Details", supplier.get("bankdetails", ""))

    if st.button("Submit"):
        updated_data = {
            "suppliertype": supplier_type,
            "country": country,
            "city": city,
            "address": address,
            "postalcode": postal_code,
            "contactname": contact_name,
            "contactphone": contact_phone,
            "paymentterms": payment_terms,
            "bankdetails": bank_details,
        }

        # Update supplier details in DB
        update_supplier(supplier["supplierid"], updated_data)
        st.success("Profile updated successfully! Please continue to the dashboard.")
        st.experimental_rerun()  # Refresh the page to show the dashboard

def show_supplier_dashboard(supplier):
    """Displays the supplier dashboard."""
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")

    # Logout button
    if st.button("Log out"):
        st.logout()
        st.experimental_rerun()

if __name__ == "__main__":
    main()
