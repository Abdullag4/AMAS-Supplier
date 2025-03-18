import streamlit as st
import io
from PIL import Image
from purchase_order.PO_db import get_archived_purchase_orders, get_purchase_order_items

def show_archived_po_page(supplier):
    """Displays archived (Declined or Completed) purchase orders."""
    st.subheader("📂 Archived Purchase Orders")

    # Fetch archived purchase orders
    archived_orders = get_archived_purchase_orders(supplier["supplierid"])

    if not archived_orders:
        st.info("No archived purchase orders.")
        return

    # Display archived purchase orders
    for po in archived_orders:
        with st.expander(f"PO ID: {po['poid']} | Status: {po['status']}"):
            st.write(f"**Order Date:** {po['orderdate']}")
            st.write(f"**Expected Delivery:** {po['expecteddelivery'] if po['expecteddelivery'] else 'Not Set'}")
            st.write(f"**Status:** {po['status']}")

            # Show ordered items
            items = get_purchase_order_items(po["poid"])
            if items:
                st.subheader("Ordered Items")
                for item in items:
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if item["itempicture"]:  
                            try:
                                image = Image.open(io.BytesIO(item["itempicture"]))
                                st.image(image, width=100, caption=item["itemnameenglish"])
                            except Exception:
                                st.warning("Error displaying image.")
                        else:
                            st.write("No Image")

                    with col2:
                        st.write(f"**{item['itemnameenglish']}**")
                        st.write(f"**Ordered Quantity:** {item['orderedquantity']}")
                        st.write(f"**Estimated Price:** {item['estimatedprice'] or 'N/A'}")
