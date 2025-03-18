import base64
import imghdr
from db_handler import run_query, run_transaction


def get_purchase_orders_for_supplier(supplier_id):
    query = """
    SELECT POID, OrderDate, ExpectedDelivery, Status
    FROM PurchaseOrders
    WHERE SupplierID = %s AND Status IN ('Pending', 'Accepted', 'Shipping')
    ORDER BY OrderDate DESC;
    """
    return run_query(query, (supplier_id,))

def get_archived_purchase_orders(supplier_id):
    query = """
    SELECT POID, OrderDate, ExpectedDelivery, Status, SupplierNote
    FROM PurchaseOrders
    WHERE SupplierID = %s AND Status IN ('Declined', 'Delivered', 'Completed')
    ORDER BY OrderDate DESC;
    """
    return run_query(query, (supplier_id,))

def update_purchase_order_status(poid, status, expected_delivery=None, supplier_note=None):
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

    # Determine correct image MIME type dynamically
    for item in results:
        if item["itempicture"]:
            # Determine MIME type using imghdr
            img_bytes = item["itempicture"]
            img_data = base64.b64decode(img_bytes)
            img_type = imghdr.what(None, img_data)
            if img_type:
                mime_type = f'image/{img_type}'
            else:
                mime_type = 'image/jpeg'  # fallback type

            item["itempicture"] = f"data:{mime_type};base64,{img_bytes}"
        else:
            item["itempicture"] = None

    return results
