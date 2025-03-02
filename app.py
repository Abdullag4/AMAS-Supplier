import streamlit as st
from sup_signin import sign_in_with_google

def main():
    st.title("AMAS Supplier App")
    
    # Call the sign-in function.
    # If the user is not signed in, this function will trigger the sign‑in flow.
    user_info = sign_in_with_google()
    
    # If user_info is still None (not signed in), halt further execution.
    if not user_info:
        st.stop()
    
    # Once the user is signed in, display the main dashboard.
    st.write(f"Welcome, {user_info['name']}!")
    st.write("This is your supplier dashboard. [Add your app content here...]")

if __name__ == "__main__":
    main()
