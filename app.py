import streamlit as st
from sup_signin import sign_in_with_google

def main():
    st.title("AMAS Supplier App")
    
    user_info = sign_in_with_google()
    if not user_info:
        st.stop()  # Stop execution until sign in is complete.
    
    st.write(f"Welcome, {user_info['name']}!")
    st.write("This is your supplier dashboard. [Add your app content here...]")

if __name__ == "__main__":
    main()
