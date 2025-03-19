import streamlit as st
import io
from PIL import Image
import pandas as pd
from purchase_order.po_handler import (
    get_purchase_orders_for_supplier,
    update_purchase_order_status,
    get_purchase_order_items,
    update_po_item_proposal
)

def show_purchase_orders_page(supplier):
    """Displays active purchase orders for the supplier in an HTML table with images,
       plus a 'Modify & Propose' option for each item."""
    st.subheader("📦 Track Purchase Orders")

    # For controlling the 'decline reason' flow
    if "decline_po_show_reason" not in st.session_state:
        st.session_state["decline_po_show_reason"] = {}

    # For controlling the 'modify' mode for each item
    if "modify_item_proposal" not in st.session_state:
        st.session_state["modify_item_proposal"] = {}

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

            items = get_purchase_order_items(po["poid"])
            if items:
                st.subheader("Ordered Items")

                # Build DataFrame rows including proposed columns
                rows = []
                for item in items:
                    # Build HTML for image
                    if item["itempicture"]:
                        img_html = f'<img src="{item["itempicture"]}" width="50" />'
                    else:
                        img_html = "No Image"

                    # Proposed data placeholders
                    # If columns are null, show placeholders in table
                    proposed_qty = item.get("supproposedquantity") or ""
                    proposed_price = item.get("supproposedprice") or ""
                    proposed_deliv = item.get("supproposeddelivery") or ""
                    proposed_note = item.get("supitemnote") or ""

                    rows.append({
                        "ItemID": item["itemid"],
                        "Picture": img_html,
                        "Item Name": item["itemnameenglish"],
                        "Ordered Qty": item["orderedquantity"],
                        "Est. Price": item["estimatedprice"] or "N/A",
                        "SupQty": proposed_qty,
                        "SupPrice": proposed_price,
                        "SupDelivery": proposed_deliv,
                        "SupNote": proposed_note
                    })

                df = pd.DataFrame(rows, columns=[
                    "ItemID", "Picture", "Item Name", 
                    "Ordered Qty", "Est. Price",
                    "SupQty", "SupPrice", "SupDelivery", "SupNote"
                ])
                df_html = df.to_html(escape=False, index=False)
                st.markdown(df_html, unsafe_allow_html=True)

                # Let the supplier choose an item to "Modify & Propose"
                st.write("**Modify & Propose Changes**")
                item_id_options = [str(it["itemid"]) for it in items]
                selected_itemid = st.selectbox("Select an item to modify:", item_id_options, key=f"item_select_{po['poid']}")

                if selected_itemid:
                    selected_itemid = int(selected_itemid)
                    # We'll show input fields for that item
                    col1, col2, col3, col4 = st.columns(4)
                    sup_qty_input = col1.number_input("Proposed Qty", min_value=0, value=0, key=f"sup_qty_{po['poid']}_{selected_itemid}")
                    sup_price_input = col2.number_input("Proposed Price", min_value=0.0, value=0.0, step=0.1, key=f"sup_price_{po['poid']}_{selected_itemid}")
                    sup_delivery_input = col3.date_input("Proposed Delivery", key=f"sup_deliv_{po['poid']}_{selected_itemid}")
                    sup_note_input = col4.text_input("Note", key=f"sup_note_{po['poid']}_{selected_itemid}")

                    if st.button("Submit Proposal", key=f"submit_prop_{po['poid']}_{selected_itemid}"):
                        # Update the DB with these proposals
                        update_po_item_proposal(
                            poid=po["poid"],
                            itemid=selected_itemid,
                            sup_qty=sup_qty_input,
                            sup_price=sup_price_input,
                            sup_delivery=sup_delivery_input,
                            sup_note=sup_note_input
                        )
                        st.success(f"Proposed changes saved for ItemID {selected_itemid}!")
                        st.rerun()

            # Supplier Actions (Accept, Decline, etc.)
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
