import streamlit as st

def main():
    st.title("AMAS Supplier App")
    st.subheader("Welcome to the AMAS Supplier App (initial setup)")
    
    st.write("This app will allow suppliers to:")
    st.write("- Log in via Google")
    st.write("- View and manage their purchase orders")
    st.write("- Confirm deliveries and more...")
    
    st.info("Stay tuned! We’ll add more functionality step by step.")

if __name__ == "__main__":
    main()
