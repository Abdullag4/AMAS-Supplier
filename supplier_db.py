from db_handler import run_query

def get_supplier_by_email(email):
    """
    Retrieve a supplier record by contact email.
    Returns a dict if found, or None if not.
    """
    query = "SELECT * FROM supplier WHERE contactemail = %s"
    result = run_query(query, (email,))
    if result and len(result) > 0:
        return result[0]
    return None

def create_supplier(suppliername, contactemail,
                    suppliertype=None, country=None,
                    city=None, address=None, postalcode=None,
                    contactname=None, contactphone=None,
                    paymentterms=None, bankdetails=None):
    """
    Insert a new supplier record with a RETURNING clause to get the new row.
    Returns the newly created row as a dict, or None if something fails.
    """
    query = """
    INSERT INTO supplier (
        suppliername, suppliertype, country, city, address,
        postalcode, contactname, contactphone, contactemail,
        paymentterms, bankdetails
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING supplierid, suppliername, contactemail;
    """
    params = (
        suppliername,
        suppliertype,
        country,
        city,
        address,
        postalcode,
        contactname,
        contactphone,
        contactemail,
        paymentterms,
        bankdetails
    )
    result = run_query(query, params)
    if result:
        return result[0]  # The newly inserted row
    return None

def get_or_create_supplier(suppliername, contactemail):
    """
    If a supplier with 'contactemail' exists, return it.
    Otherwise, create one with minimal info (suppliername, contactemail).
    """
    supplier = get_supplier_by_email(contactemail)
    if supplier:
        return supplier
    else:
        new_supplier = create_supplier(suppliername, contactemail)
        return new_supplier
