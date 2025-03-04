import streamlit as st

def main():
    st.title("AMAS Supplier App (OIDC)")

    # 1. Check if user is logged in
    if not st.experimental_user.is_logged_in:
        # 2. Show a login button for Google
        st.write("You are not logged in.")
        if st.button("Log in with Google"):
            # This calls the OIDC login flow using the config in [auth] in secrets.toml
            st.login()
        st.stop()  # Stop execution until user is logged in

    # 3. If we reach here, user is logged in. Show a logout button.
    if st.button("Log out"):
        st.logout()

    # 4. Display some user info
    st.markdown(f"**Welcome** {st.experimental_user.name or ''}!")
    st.markdown(f"**Email**: {st.experimental_user.email or ''}")
    st.markdown("Here is your supplier dashboard...")

if __name__ == "__main__":
    main()
