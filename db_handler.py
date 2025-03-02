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
    Execute a SQL query (typically a SELECT) and return all rows.

    Args:
        query (str): The SQL query to run.
        params (tuple or dict, optional): Parameters to pass with the query.

    Returns:
        list[dict]: List of rows as dictionaries.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                # Return rows if the query is a SELECT
                if query.strip().lower().startswith("select"):
                    return cur.fetchall()
                else:
                    conn.commit()
    except Exception as e:
        st.error(f"Error executing query: {e}")
        raise
    finally:
        conn.close()

def run_transaction(query, params=None):
    """
    Execute a SQL query that modifies data (INSERT, UPDATE, DELETE)
    and commit the changes.

    Args:
        query (str): The SQL query to run.
        params (tuple or dict, optional): Parameters to pass with the query.
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
