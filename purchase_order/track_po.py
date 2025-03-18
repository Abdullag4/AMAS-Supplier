import streamlit as st
import io
from PIL import Image
import pandas as pd
from purchase_order.po_handler import (
    get_purchase_orders_for_supplier, 
    update_purchase_order_status, 
    get_purchase_order_items
)

def show_purchase_orders_page(supplier):
    """Displays active purchase orders for the supplier in an HTML table with images."""
    st.subheader("📦 Track Purchase Orders")

    # For controlling the 'decline reason' flow
    if "decline_po_show_reason" not in st.session_state:
        st.session_state["decline_po_show_reason"] = {}

    # Fetch active POs
    purchase_orders = get_purchase_orders_for_supplier(supplier["supplierid"])
    if not purchase_orders:
        st.info("No active purchase orders.")
        return

    for po in purchase_orders:
        with st.expander(f"PO ID: {po['poid']} | Status: {po['status']}"):
            st.write(f"**Order Date:** {po['orderdate']}")
            st.write(f"**Expected Delivery:** {po['expecteddelivery'] or 'Not Set'}")
            st.write(f"**Status:** {po['status']}")

            # Show items in a table with images in columns
            items = get_purchase_order_items(po["poid"])
            if items:
                st.subheader("Ordered Items (with Images in Table)")

                rows = []
                for item in items:
                    # item["itempicture"] is 'data:image/png;base64,<data>' or None
                    if item["itempicture"]:
                        # Build an <img> tag for the table cell
                        img_html = f'<img src="{item["itempicture"]}" width="80" />'
                    else:
                        img_html = "No Image"

                    rows.append({
                        "Picture": img_html,
                        "Item Name": item["itemnameenglish"],
                        "Ordered Qty": item["orderedquantity"],
                        "Estimated Price": item["estimatedprice"] or "N/A"
                    })

                df = pd.DataFrame(rows, columns=["Picture", "Item Name", "Ordered Qty", "Estimated Price"])
                df_html = df.to_html(escape=False, index=False)  # escape=False to render <img> tags
                st.markdown(df_html, unsafe_allow_html=True)

            # Supplier Actions
            if po["status"] == "Pending":
                st.subheader("Respond to Order")
                col1, col2 = st.columns(2)

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

                # Decline with reason
                with col2:
                    if not st.session_state["decline_po_show_reason"].get(po["poid"], False):
                        # Show "Decline Order" button
                        if st.button("Decline Order", key=f"decline_{po['poid']}"):
                            st.session_state["decline_po_show_reason"][po["poid"]] = True
                            st.rerun()
                    else:
                        # Show text area for reason
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
