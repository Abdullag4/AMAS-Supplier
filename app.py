import streamlit as st
from sup_signin import sign_in_with_google

def main():
    st.title("AMAS Supplier App")
    
    # If user is not signed in, display the sign-in flow.
    if "user_info" not in st.session_state:
        user_info = sign_in_with_google()
        if not user_info:
            st.stop()  # Stop execution until sign in is complete

    # If user is signed in, display the main dashboard/app content.
    st.write(f"Welcome, {st.session_state['user_info']['name']}!")
    st.write("This is your supplier dashboard. [Add your app content here...]")

if __name__ == "__main__":
    main()
