import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# Retrieve the Neon DSN from Streamlit secrets
NEON_DSN = st.secrets["neon"]["dsn"]

def get_connection():
    """
    Establish and return a new connection to the Neon PostgreSQL database
    using the DSN provided in the Streamlit secrets.
    """
    try:
        conn = psycopg2.connect(NEON_DSN, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        raise

def run_query(query, params=None):
    """
    Execute a SQL query. If it's a SELECT or includes a RETURNING clause,
    return the resulting rows as a list of dictionaries.
    Otherwise, commit and return None.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                lower_query = query.strip().lower()
                # If SELECT or returning, fetch rows
                if lower_query.startswith("select") or " returning " in lower_query:
                    return cur.fetchall()
                else:
                    conn.commit()
                    return None
    except Exception as e:
        st.error(f"Error executing query: {e}")
        raise
    finally:
        conn.close()

def run_transaction(query, params=None):
    """
    Execute a SQL query that modifies data (INSERT, UPDATE, DELETE)
    and commit the changes.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
            conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Transaction failed: {e}")
        raise
    finally:
        conn.close()
