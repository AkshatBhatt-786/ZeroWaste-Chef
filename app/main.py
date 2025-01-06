import streamlit as st


# ---------------------- Modern Auth Page ----------------------
class ModernAuthPage:
    """Modern authentication page with clean design and styling."""

    def __init__(self):
        self.title = "🍴 ZeroWaste Chef - Authentication"
        self.page_title = "Welcome to ZeroWaste Chef"
        self.subtitle = "Save food, save money, save the planet!"
        self.button_style = """
            <style>
            .css-18e3th9 {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                border: 1px solid #4CAF50;
                padding: 12px 20px;
                font-size: 18px;
                font-weight: bold;
            }
            .css-18e3th9:hover {
                background-color: #45a049;
                border-color: #45a049;
            }
            </style>
        """
        st.markdown(self.button_style, unsafe_allow_html=True)

    def show_auth_page(self):
        """Displays the authentication page with login and signup options."""

        # Move this to the top of the script as the first Streamlit function call
        st.set_page_config(page_title=self.page_title, layout="centered")

        # Centering the title and subtitle
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>{self.page_title}</h1>",
                        unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #555;'>{self.subtitle}</p>", unsafe_allow_html=True)

        # Spacer
        st.write("\n" * 2)

        # Navigation for authentication
        login_signup_option = st.radio("", ("Login", "Sign Up"), key="login_signup", label_visibility="collapsed")

        if login_signup_option == "Login":
            self.show_login_form()
        elif login_signup_option == "Sign Up":
            self.show_signup_form()

    def show_login_form(self):
        """Displays the login form with modern styling."""
        with st.container():
            st.subheader("Login to Your Account", anchor="login")
            st.write("\n")

            username = st.text_input("Username", placeholder="Enter your username", key="login_username",
                                     label_visibility="collapsed")
            password = st.text_input("Password", type="password", placeholder="Enter your password",
                                     key="login_password", label_visibility="collapsed")

            login_button = st.button("Login")
            self.styled_button(login_button)

            if login_button:
                if username and password:
                    # Simulating login validation
                    st.success("Logged in successfully!")
                    # Redirect to another page or set session state for user
                else:
                    st.error("Please enter both username and password.")

    def show_signup_form(self):
        """Displays the sign-up form with modern styling."""
        with st.container():
            st.subheader("Create Your Account", anchor="signup")
            st.write("\n")

            username = st.text_input("Username", placeholder="Choose a username", key="signup_username",
                                     label_visibility="collapsed")
            password = st.text_input("Password", type="password", placeholder="Choose a password",
                                     key="signup_password", label_visibility="collapsed")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password",
                                             key="confirm_password", label_visibility="collapsed")

            signup_button = st.button("Sign Up")
            self.styled_button(signup_button)

            if signup_button:
                if username and password and password == confirm_password:
                    # Simulating user registration
                    st.success("Registration successful! You can now log in.")
                elif password != confirm_password:
                    st.error("Passwords do not match. Please try again.")
                else:
                    st.error("Please fill out all fields.")

    def styled_button(self, button):
        """Apply custom styles for button."""
        if button:
            st.markdown(f"""
            <style>
                .css-1emrehy.edgvbvh3 {{
                    padding: 12px 24px;
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                .css-1emrehy.edgvbvh3:hover {{
                    background-color: #45a049;
                    border-color: #45a049;
                }}
            </style>
            """, unsafe_allow_html=True)


# ---------------------- Main Function ----------------------
if __name__ == "__main__":
    # Call `st.set_page_config()` here as the first Streamlit command in the script
    st.set_page_config(page_title="ZeroWaste Chef", layout="centered")

    # Initialize and display the auth page
    auth_page = ModernAuthPage()
    auth_page.show_auth_page()
