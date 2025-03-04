from db_handler import run_query

def get_supplier_by_email(email):
    """Retrieve supplier record by email."""
    query = "SELECT * FROM supplier WHERE contactemail = %s"
    result = run_query(query, (email,))
    return result[0] if result else None

def create_supplier(suppliername, contactemail):
    """Insert a new supplier record with minimal default values."""
    query = """
    INSERT INTO supplier (
        suppliername, contactemail, suppliertype, country, city,
        address, postalcode, contactname, contactphone, paymentterms, bankdetails
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING supplierid, suppliername, contactemail;
    """
    params = (suppliername, contactemail, None, None, None, None, None, None, None, None, None)
    result = run_query(query, params)
    return result[0] if result else None

def get_or_create_supplier(suppliername, contactemail):
    """Fetch supplier by email; create if not exists."""
    supplier = get_supplier_by_email(contactemail)
    return supplier if supplier else create_supplier(suppliername, contactemail)

def update_supplier(supplierid, updated_data):
    """Update supplier record with new details."""
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
        updated_data["suppliertype"],
        updated_data["country"],
        updated_data["city"],
        updated_data["address"],
        updated_data["postalcode"],
        updated_data["contactname"],
        updated_data["contactphone"],
        updated_data["paymentterms"],
        updated_data["bankdetails"],
        supplierid,
    )
    run_query(query, params)
