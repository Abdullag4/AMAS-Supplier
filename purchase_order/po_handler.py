from db_handler import run_query, run_transaction

def get_purchase_orders_for_supplier(supplier_id):
    """
    Retrieves ONLY active purchase orders (Pending, Accepted, Shipping)
    assigned to a specific supplier.
    """
    query = """
    SELECT 
        POID, 
        OrderDate, 
        ExpectedDelivery, 
        Status
    FROM PurchaseOrders
    WHERE SupplierID = %s 
      AND Status IN ('Pending', 'Accepted', 'Shipping')
    ORDER BY OrderDate DESC;
    """
    return run_query(query, (supplier_id,))

def get_archived_purchase_orders(supplier_id):
    """
    Retrieves archived purchase orders (Declined, Delivered, Completed).
    """
    query = """
    SELECT 
        POID, 
        OrderDate, 
        ExpectedDelivery, 
        Status,
        SupplierNote
    FROM PurchaseOrders
    WHERE SupplierID = %s 
      AND Status IN ('Declined', 'Delivered', 'Completed')
    ORDER BY OrderDate DESC;
    """
    return run_query(query, (supplier_id,))

def update_purchase_order_status(poid, status, expected_delivery=None, supplier_note=None):
    """
    Updates the status of a purchase order.
    - If `expected_delivery` is provided, updates ExpectedDelivery.
    - If `supplier_note` is provided, updates SupplierNote (usually when declining).
    """
    query = """
    UPDATE PurchaseOrders
    SET 
        Status = %s, 
        ExpectedDelivery = COALESCE(%s, ExpectedDelivery),
        SupplierNote = COALESCE(%s, SupplierNote)
    WHERE POID = %s;
    """
    try:
        run_transaction(query, (status, expected_delivery, supplier_note, poid))
    except Exception as e:
        print(f"🚨 Error updating PO {poid}: {e}")

def get_purchase_order_items(poid):
    """
    Retrieves all items associated with a purchase order, including:
    - Item Name (English)
    - Base64-encoded Item Image (no prefix yet)
    - Ordered Quantity
    - Estimated Price
    """
    query = """
    SELECT 
        i.ItemID, 
        i.ItemNameEnglish, 
        encode(i.ItemPicture, 'base64') AS ItemPicture,
        poi.OrderedQuantity, 
        poi.EstimatedPrice
    FROM PurchaseOrderItems poi
    JOIN Item i ON poi.ItemID = i.ItemID
    WHERE poi.POID = %s;
    """
    results = run_query(query, (poid,))

    # Convert images to "data:image/jpg;base64,..." format for Streamlit
    for item in results:
        # If not empty, add the prefix for direct <img src="...">
        if item["itempicture"]:
            item["itempicture"] = f"data:image/png;base64,{item['itempicture']}"
        else:
            item["itempicture"] = None

    return results
