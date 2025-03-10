import streamlit as st
from sup_signin import sign_in_with_google
from supplier_db import get_or_create_supplier
from home import show_home_page
from purchase_order.PO import show_purchase_orders_page  # 🔥 Updated import path

def main():
    st.title("AMAS Supplier App")

    # 1. Sign in with Google
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()

    # 2. Get supplier record
    supplier = get_or_create_supplier(user_info["email"])

    # 3. Sidebar Navigation
    st.sidebar.title("Navigation")
    menu_choice = st.sidebar.radio("Go to:", ["Home", "Purchase Orders", "Supplier Dashboard"])

    # 4. Show the selected page
    if menu_choice == "Home":
        show_home_page()
    elif menu_choice == "Purchase Orders":
        show_purchase_orders_page(supplier)  # 🔥 Uses the updated import
    else:
        show_supplier_dashboard(supplier)

def show_supplier_dashboard(supplier):
    """Displays the supplier dashboard."""
    st.write(f"Welcome, **{supplier['suppliername']}**!")
    st.write(f"Your Supplier ID is: **{supplier['supplierid']}**")

    # Logout button
    if st.button("Log out"):
        st.logout()
        st.rerun()

if __name__ == "__main__":
    main()
