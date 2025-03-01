import streamlit as st
from sup_signin import sign_in_with_google

def main():
    st.title("AMAS Supplier App")

    # Check if user info is already in session state
    if "user_info" not in st.session_state:
        user_info = sign_in_with_google()
        if user_info:
            st.session_state["user_info"] = user_info
    else:
        st.success(f"Welcome back, {st.session_state['user_info']['name']}!")
        # Add your dashboard or additional pages here

if __name__ == "__main__":
    main()
