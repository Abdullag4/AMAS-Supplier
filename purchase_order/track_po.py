import streamlit as st
import io
from PIL import Image
from purchase_order.po_handler import (
    get_purchase_orders_for_supplier, 
    update_purchase_order_status, 
    get_purchase_order_items
)

def show_purchase_orders_page(supplier):
    """Displays active purchase orders for the supplier."""
    st.subheader("📦 Track Purchase Orders")

    # Fetch active purchase orders (Pending, Accepted, Shipping)
    purchase_orders = get_purchase_orders_for_supplier(supplier["supplierid"])
    if not purchase_orders:
        st.info("No active purchase orders.")
        return

    # Dictionary to track the current PO ID for which the user clicked "Decline"
    # so we can show the reason text area inline.
    if "decline_po_show_reason" not in st.session_state:
        st.session_state["decline_po_show_reason"] = {}

    # Display purchase orders
    for po in purchase_orders:
        with st.expander(f"PO ID: {po['poid']} | Status: {po['status']}"):
            st.write(f"**Order Date:** {po['orderdate']}")
            st.write(f"**Expected Delivery:** {po['expecteddelivery'] or 'Not Set'}")
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

                # Accept Order
                with col1:
                    if st.button("Accept Order", key=f"accept_{po['poid']}"):
                        expected_delivery = st.date_input(
                            f"Expected Delivery Date (PO {po['poid']})",
                            key=f"date_{po['poid']}"
                        )
                        if expected_delivery:
                            update_purchase_order_status(
                                poid=po["poid"],
                                status="Accepted",
                                expected_delivery=expected_delivery
                            )
                            st.success("Order Accepted!")
                            st.rerun()

                # Decline Order
                with col2:
                    if not st.session_state["decline_po_show_reason"].get(po["poid"], False):
                        # Show "Decline Order" button
                        if st.button("Decline Order", key=f"decline_{po['poid']}"):
                            # Mark that we want to show the text area for this PO
                            st.session_state["decline_po_show_reason"][po["poid"]] = True
                            st.rerun()
                    else:
                        # We are showing the text area for reason
                        st.write("**Reason for Declination**")
                        decline_note = st.text_area("Please provide a reason:", key=f"note_{po['poid']}")

                        confirm_col, cancel_col = st.columns(2)
                        with confirm_col:
                            if st.button("Confirm Decline", key=f"confirm_decline_{po['poid']}"):
                                update_purchase_order_status(
                                    poid=po["poid"],
                                    status="Declined",
                                    supplier_note=decline_note
                                )
                                st.warning("Order Declined!")
                                # Reset the session flag
                                st.session_state["decline_po_show_reason"][po["poid"]] = False
                                st.rerun()

                        with cancel_col:
                            if st.button("Cancel", key=f"cancel_decline_{po['poid']}"):
                                st.session_state["decline_po_show_reason"][po["poid"]] = False
                                st.rerun()

            elif po["status"] == "Accepted":
                if st.button("Mark as Shipping", key=f"ship_{po['poid']}"):
                    update_purchase_order_status(poid=po["poid"], status="Shipping")
                    st.info("Order marked as Shipping.")
                    st.rerun()

            elif po["status"] == "Shipping":
                if st.button("Mark as Delivered", key=f"delivered_{po['poid']}"):
                    update_purchase_order_status(poid=po["poid"], status="Delivered")
                    st.success("Order marked as Delivered.")
                    st.rerun()
