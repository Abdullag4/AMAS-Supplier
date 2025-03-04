from db_handler import run_query

# List of required fields with their human-readable labels
SUPPLIER_FIELDS = {
    "suppliertype": "Supplier Type",
    "country": "Country",
    "city": "City",
    "address": "Address",
    "postalcode": "Postal Code",
    "contactname": "Contact Name",
    "contactphone": "Contact Phone",
    "paymentterms": "Payment Terms",
    "bankdetails": "Bank Details"
}

def get_supplier_by_email(email):
    """Retrieve supplier record by email."""
    query = "SELECT * FROM supplier WHERE contactemail = %s"
    result = run_query(query, (email,))
    return result[0] if result else None

def create_supplier(suppliername, contactemail):
    """Insert a new supplier record with minimal data."""
    query = """
    INSERT INTO supplier (suppliername, contactemail)
    VALUES (%s, %s)
    RETURNING supplierid, suppliername, contactemail;
    """
    params = (suppliername, contactemail)
    result = run_query(query, params)
    return result[0] if result else None

def get_or_create_supplier(suppliername, contactemail):
    """Fetch supplier by email; create if not exists."""
    supplier = get_supplier_by_email(contactemail)
    return supplier if supplier else create_supplier(suppliername, contactemail)

def get_missing_fields(supplier):
    """
    Identify missing required fields for a supplier.
    Returns a list of missing fields with labels.
    """
    missing_fields = {
        key: label for key, label in SUPPLIER_FIELDS.items() if not supplier.get(key)
    }
    return missing_fields

def get_supplier_form_structure():
    """
    Returns a structured dictionary defining the supplier form.
    - Defines the labels for each field.
    - Defines input types (text, select, etc.) for modularity.
    """
    return {
        "suppliertype": {"label": "Supplier Type", "type": "select", "options": ["Manufacturer", "Distributor", "Retailer", "Other"]},
        "country": {"label": "Country", "type": "text"},
        "city": {"label": "City", "type": "text"},
        "address": {"label": "Address", "type": "text"},
        "postalcode": {"label": "Postal Code", "type": "text"},
        "contactname": {"label": "Contact Name", "type": "text"},
        "contactphone": {"label": "Contact Phone", "type": "text"},
        "paymentterms": {"label": "Payment Terms", "type": "textarea"},
        "bankdetails": {"label": "Bank Details", "type": "textarea"}
    }

def save_supplier_details(supplierid, form_data):
    """Updates supplier details based on submitted form data."""
    query = """
    UPDATE supplier
    SET
        suppliertype = %s,
        country = %s,
        city = %s,
        address = %s,
        postalcode = %s,
        contactname = %s,
        contactphone = %s,
        paymentterms = %s,
        bankdetails = %s
    WHERE supplierid = %s
    """
    params = (
        form_data["suppliertype"],
        form_data["country"],
        form_data["city"],
        form_data["address"],
        form_data["postalcode"],
        form_data["contactname"],
        form_data["contactphone"],
        form_data["paymentterms"],
        form_data["bankdetails"],
        supplierid,
    )
    run_query(query, params)
