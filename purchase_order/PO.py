import streamlit as st
import base64
from purchase_order.PO_db import get_active_purchase_orders, get_purchase_order_items, update_purchase_order_status

def show_track_po_page(supplier):
    """Displays only active purchase orders assigned to the supplier."""
    st.title("📦 Track Purchase Orders")

    purchase_orders = get_active_purchase_orders(supplier["supplierid"])

    if not purchase_orders:
        st.info("No active purchase orders.")
        return

    for po in purchase_orders:
        with st.expander(f"PO ID: {po['poid']} | Status: {po['status']}"):
            st.write(f"**Order Date:** {po['orderdate']}")
            st.write(f"**Expected Delivery:** {po['expecteddelivery'] if po['expecteddelivery'] else 'Not Set'}")
            st.write(f"**Status:** {po['status']}")

            items = get_purchase_order_items(po["poid"])
            if items:
                st.subheader("Ordered Items")
                for item in items:
                    col1, col2 = st.columns([1, 3])

                    # Convert binary image data to Base64 for display
                    item_image = None
                    if item["itempicture"]:
                        try:
                            item_image = base64.b64encode(item["itempicture"]).decode("utf-8")
                            item_image = f"data:image/png;base64,{item_image}"
                        except Exception as e:
                            st.warning(f"Error displaying image for {item['itemnameenglish']}: {e}")

                    with col1:
                        if item_image:
                            st.image(item_image, width=100, caption=item["itemnameenglish"])
                        else:
                            st.write("No Image Available")

                    with col2:
                        st.write(f"**{item['itemnameenglish']}**")
                        st.write(f"Quantity: {item['orderedquantity']}")
                        st.write(f"Estimated Price: {item['estimatedprice'] or 'N/A'}")

            if po["status"] == "Pending":
                if st.button(f"✅ Accept Order {po['poid']}", key=f"accept_{po['poid']}"):
                    expected_delivery = st.date_input(f"Expected Delivery Date (PO {po['poid']})", key=f"date_{po['poid']}")
                    if expected_delivery:
                        update_purchase_order_status(po["poid"], "Accepted", expected_delivery)
                        st.success("Order Accepted!")
                        st.rerun()

                if st.button(f"❌ Decline Order {po['poid']}", key=f"decline_{po['poid']}"):
                    update_purchase_order_status(po["poid"], "Declined")
                    st.warning("Order Declined!")
                    st.rerun()

            elif po["status"] == "Accepted":
                if st.button(f"🚚 Mark as Shipping {po['poid']}", key=f"ship_{po['poid']}"):
                    update_purchase_order_status(po["poid"], "Shipping")
                    st.info("Order marked as Shipping.")
                    st.rerun()

            elif po["status"] == "Shipping":
                if st.button(f"📦 Mark as Delivered {po['poid']}", key=f"delivered_{po['poid']}"):
                    update_purchase_order_status(po["poid"], "Delivered")
                    st.success("Order marked as Delivered.")
                    st.rerun()
