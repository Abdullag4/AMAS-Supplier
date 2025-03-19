import base64
import io
from PIL import Image
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
    - Item Picture (auto-detected format)
    - Ordered Quantity, Estimated Price
    - Proposed columns: SupProposedQuantity, SupProposedPrice, SupProposedDelivery, SupItemNote
    """
    query = """
    SELECT 
        i.ItemID,
        i.ItemNameEnglish,
        encode(i.ItemPicture, 'base64') AS ItemPicture,
        poi.OrderedQuantity,
        poi.EstimatedPrice,
        poi.SupProposedQuantity,
        poi.SupProposedPrice,
        poi.SupProposedDelivery,
        poi.SupItemNote
    FROM PurchaseOrderItems poi
    JOIN Item i ON poi.ItemID = i.ItemID
    WHERE poi.POID = %s;
    """
    results = run_query(query, (poid,))
    if not results:
        return []

    # Convert raw base64 to data URI for images
    for item in results:
        if item["itempicture"]:
            try:
                raw_base64 = item["itempicture"]
                image_bytes = base64.b64decode(raw_base64)
                img = Image.open(io.BytesIO(image_bytes))
                image_format = img.format or "PNG"  # default to PNG if format unknown

                buffer = io.BytesIO()
                img.save(buffer, format=image_format)
                reencoded_b64 = base64.b64encode(buffer.getvalue()).decode()

                # decide correct mime
                if image_format.lower() in ["jpeg", "jpg"]:
                    mime_type = "jpeg"
                elif image_format.lower() == "png":
                    mime_type = "png"
                else:
                    mime_type = "png"

                item["itempicture"] = f"data:image/{mime_type};base64,{reencoded_b64}"
            except Exception:
                item["itempicture"] = None
        else:
            item["itempicture"] = None

    return results

def update_po_item_proposal(poid, itemid, sup_qty, sup_price, sup_delivery, sup_note):
    """
    Saves the supplier's proposed changes for a specific item in PurchaseOrderItems table.
    (SupProposedQuantity, SupProposedPrice, SupProposedDelivery, SupItemNote)
    """
    query = """
    UPDATE PurchaseOrderItems
    SET 
        SupProposedQuantity = %s,
        SupProposedPrice = %s,
        SupProposedDelivery = %s,
        SupItemNote = %s
    WHERE POID = %s
      AND ItemID = %s;
    """
    run_transaction(query, (sup_qty, sup_price, sup_delivery, sup_note, poid, itemid))
