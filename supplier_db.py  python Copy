from db_handler import run_query

def get_supplier_by_email(email):
    """
    Retrieve a supplier record by contact email.
    
    Args:
        email (str): The supplier's contact email.
        
    Returns:
        dict or None: Supplier record as a dictionary if found; otherwise, None.
    """
    query = "SELECT * FROM supplier WHERE contactemail = %s"
    result = run_query(query, (email,))
    if result and len(result) > 0:
        return result[0]
    return None

def create_supplier(suppliername, contactemail, suppliertype=None, country=None,
                    city=None, address=None, postalcode=None, contactname=None,
                    contactphone=None, paymentterms=None, bankdetails=None):
    """
    Insert a new supplier record into the supplier table.
    
    Note:
        The supplierid column is auto-generated, so it is not provided.
    
    Args:
        suppliername (str): The name of the supplier.
        contactemail (str): The supplier's contact email.
        suppliertype, country, city, address, postalcode, contactname, 
        contactphone, paymentterms, bankdetails (str, optional): Additional supplier details.
        
    Returns:
        dict or None: The newly created supplier record (with supplierid) as a dictionary, or None if failed.
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
        return result[0]
    return None

def get_or_create_supplier(suppliername, contactemail):
    """
    Retrieves a supplier by contact email, and if none exists,
    creates a new supplier record with the given minimal information.
    
    Args:
        suppliername (str): The supplier's name (from the Google sign-in, for example).
        contactemail (str): The supplier's contact email.
        
    Returns:
        dict: The supplier record.
    """
    supplier = get_supplier_by_email(contactemail)
    if supplier:
        return supplier
    else:
        # Create a new supplier record using minimal details.
        new_supplier = create_supplier(suppliername, contactemail)
        return new_supplier
