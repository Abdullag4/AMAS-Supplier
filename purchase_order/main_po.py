import streamlit as st
from purchase_order.PO import show_track_po_page
from purchase_order.archived_po import show_archived_po_page

def show_purchase_orders_page(supplier):
    """Manages the Purchase Order tabs."""
    st.title("Purchase Orders")

    # Tabs for Active & Archived POs
    tab1, tab2 = st.tabs(["📦 Track PO", "📂 Archived PO"])

    with tab1:
        show_track_po_page(supplier)  # Shows active POs

    with tab2:
        show_archived_po_page(supplier)  # Shows archived POs
