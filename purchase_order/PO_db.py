from db_handler import run_query

def get_purchase_orders_for_supplier(supplier_id):
    """
    Retrieves all purchase orders assigned to a specific supplier.
    """
    query = """
    SELECT POID, OrderDate, ExpectedDelivery, Status
    FROM PurchaseOrders
    WHERE SupplierID = %s
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
    run_query(query, (status, expected_delivery, poid))

def get_purchase_order_items(poid):
    """
    Retrieves all items associated with a purchase order, including the item name and picture.
    """
    query = """
    SELECT 
        i.ItemID, 
        i.ItemNameEnglish, 
        i.ItemPicture, 
        poi.OrderedQuantity, 
        poi.EstimatedPrice
    FROM PurchaseOrderItems poi
    JOIN Item i ON poi.ItemID = i.ItemID  -- 🔥 Join with Item table
    WHERE poi.POID = %s;
    """
    return run_query(query, (poid,))
