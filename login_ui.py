
import streamlit as st
import auth_db


def show_login_page():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #17172F, #514071);
        padding: 28px;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 24px;
    ">
        <h1 style="color: white;">🎓 College Helpdesk Bot</h1>
        <p style="color: #DDD5EE;">
            Your Campus • Your Knowledge
        </p>
    </div>
    """, unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    with login_tab:
        st.subheader("Welcome Back")

        with st.form("login_form"):
            email = st.text_input(
                "Email Address",
                placeholder="you@email.edu"
            )
            password = st.text_input(
                "Password",
                type="password"
            )
            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True
            )

        if submitted:
            user = auth_db.verify_login(email, password)

            if user:
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error(
                    "Login failed. Check your details or "
                    "contact the administrator for account approval."
                )

    with register_tab:
        st.subheader("Create Student Account")

        with st.form("register_form"):
            new_email = st.text_input(
                "Email Address",
                key="register_email"
            )
            new_password = st.text_input(
                "Password (minimum 12 characters)",
                type="password",
                key="register_password"
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )
            register = st.form_submit_button(
                "Register",
                use_container_width=True
            )

        if register:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                ok, message = auth_db.register_user(
                    new_email,
                    new_password
                )

                if ok:
                    st.success(message)
                else:
                    st.error(message)
