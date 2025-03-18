import streamlit as st
import io
from PIL import Image
from purchase_order.PO_db import get_purchase_order_items, get_purchase_orders_for_supplier, update_purchase_order_status

def show_purchase_orders_page(supplier):
    """Displays active purchase orders for the supplier."""
    st.subheader("📦 Track Purchase Orders")

    # Fetch active purchase orders (excluding archived ones)
    purchase_orders = get_purchase_orders_for_supplier(supplier["supplierid"])

    if not purchase_orders:
        st.info("No active purchase orders.")
        return

    # Display purchase orders
    for po in purchase_orders:
        if po["status"] in ["Declined", "Delivered"]:
            continue  # 🚀 Skip archived orders

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

            # Supplier Actions
            if po["status"] == "Pending":
                st.subheader("Respond to Order")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Accept Order", key=f"accept_{po['poid']}"):
                        expected_delivery = st.date_input(f"Expected Delivery Date (PO {po['poid']})", key=f"date_{po['poid']}")
                        if expected_delivery:
                            update_purchase_order_status(po["poid"], "Accepted", expected_delivery)
                            st.success("Order Accepted!")
                            st.rerun()
                with col2:
                    if st.button("Decline Order", key=f"decline_{po['poid']}"):
                        update_purchase_order_status(po["poid"], "Declined")
                        st.warning("Order Declined!")
                        st.rerun()

            elif po["status"] == "Accepted":
                if st.button("Mark as Shipping", key=f"ship_{po['poid']}"):
                    update_purchase_order_status(po["poid"], "Shipping")
                    st.info("Order marked as Shipping.")
                    st.rerun()

            elif po["status"] == "Shipping":
                if st.button("Mark as Delivered", key=f"delivered_{po['poid']}"):
                    update_purchase_order_status(po["poid"], "Delivered")
                    st.success("Order marked as Delivered.")
                    st.rerun()
