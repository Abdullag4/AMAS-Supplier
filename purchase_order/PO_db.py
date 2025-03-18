from db_handler import run_query, run_transaction

def get_purchase_orders_for_supplier(supplier_id):
    """
    Retrieves all active purchase orders assigned to a specific supplier.
    """
    query = """
    SELECT POID, OrderDate, ExpectedDelivery, Status
    FROM PurchaseOrders
    WHERE SupplierID = %s AND Status NOT IN ('Declined', 'Delivered')
    ORDER BY OrderDate DESC;
    """
    return run_query(query, (supplier_id,))

def get_archived_purchase_orders(supplier_id):
    """
    Retrieves archived purchase orders (Declined & Delivered).
    """
    query = """
    SELECT POID, OrderDate, ExpectedDelivery, Status
    FROM PurchaseOrders
    WHERE SupplierID = %s AND Status IN ('Declined', 'Delivered')
    ORDER BY OrderDate DESC;
    """
    return run_query(query, (supplier_id,))

def update_purchase_order_status(poid, status, expected_delivery=None):
    """
    Updates the status of a purchase order.
    If `expected_delivery` is provided, it updates the ExpectedDelivery field.
    """
    query = """
    UPDATE PurchaseOrders
    SET Status = %s, ExpectedDelivery = COALESCE(%s, ExpectedDelivery)
    WHERE POID = %s;
    """
    try:
        run_transaction(query, (status, expected_delivery, poid))
    except Exception as e:
        print(f"🚨 Error updating PO {poid}: {e}")

def get_purchase_order_items(poid):
    """
    Retrieves all items associated with a purchase order, including:
    - Item Name (English)
    - Item Image (decoded properly)
    - Ordered Quantity
    - Estimated Price
    """
    query = """
    SELECT 
        i.ItemID, 
        i.ItemNameEnglish, 
        encode(i.ItemPicture, 'base64') AS ItemPicture, -- 🔥 Ensure image is correctly encoded
        poi.OrderedQuantity, 
        poi.EstimatedPrice
    FROM PurchaseOrderItems poi
    JOIN Item i ON poi.ItemID = i.ItemID
    WHERE poi.POID = %s;
    """
    results = run_query(query, (poid,))
    
    # Convert image to proper format for Streamlit display
    for item in results:
        if item["itempicture"]:
            item["itempicture"] = f"data:image/png;base64,{item['itempicture']}"  # 🔥 Convert to base64 for display
    
    return results
