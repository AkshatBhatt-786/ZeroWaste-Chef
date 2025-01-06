import streamlit as st
import sqlite3
import hashlib
from icecream import ic
import os
import re
import pandas as pd
from datetime import datetime, timedelta
import sys


def get_resource_path(filepath):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, filepath)


class AuthPage:

    def __init__(self):
        self.page_title = "ZeroWaste Chef - Login"
        self.page_subtitle = "Save Food, Save Money, Save the Planet"
        self.db_name = get_resource_path("data\zero-waste_chef.db")
        self.create_user_table()

    def create_user_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_user_exists(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        result = c.fetchone()[0]
        conn.close()
        return result > 0

    def save_user(self, username, password):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, self.hash_password(password)))
        conn.commit()
        conn.close()

    def show_auth_page(self):
        if 'logged_in' not in st.session_state or not st.session_state.logged_in:
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>ZeroWaste Chef</h1>",
                            unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: #555;'>Save Food, Save Money, Save the Planet</p>",
                            unsafe_allow_html=True)

            login_signup_option = st.radio("", ["Login", "Sign Up"], index=0, horizontal=True)

            if login_signup_option == "Login":
                self.show_login_form()
            elif login_signup_option == "Sign Up":
                self.show_signup_form()
        else:
            homepage = HomePage()
            homepage.display()

    @staticmethod
    def password_validator(password):
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"
        if re.match(pattern, password):
            return True
        else:
            return False

    def verify_user(self, username, password):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        stored_password = c.fetchone()
        conn.close()

        if stored_password:
            return stored_password[0] == self.hash_password(password)
        else:
            return False


    def show_login_form(self):
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        login_button = st.button("Login", use_container_width=True)

        if login_button:
            if self.verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.stop()
            else:
                st.error("Invalid username or password.")


    def show_signup_form(self):
        st.subheader("Create a new account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        email = st.text_input("Email")
        signup_button = st.button("Sign Up", use_container_width=True)

        if signup_button:
            if not self.password_validator(password):
                st.error(
                    "Password must contain at least one number, one uppercase letter, one lowercase letter, and one special character.")
            elif self.check_user_exists(username):
                st.error(f"Username '{username}' is already taken. Please choose another one.")
            else:
                self.save_user(username, password)
                st.success(f"Account created for {username}. You can now log in!")


class HomePage:

    def __init__(self):
        self.db_name = get_resource_path("data\\zero-waste_chef.db")
        self.inventory_manager = InventoryManager(self.db_name)

    def display(self):
        st.sidebar.title("🍴 ZeroWaste Chef")
        menu = st.sidebar.radio(
            "Navigate", ("📋 Inventory", "🍳 Recipe Suggestions", "📊 Impact Tracker")
        )

        st.title("ZeroWaste Chef 🌍")
        st.write("Save food, save money, save the planet!")

        if menu == "📋 Inventory":
            self.inventory_manager.display()


class InventoryManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_inventory_table()

    def create_inventory_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY,
                item_name TEXT,
                quantity REAL,
                unit TEXT,
                expiry_date TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_item(self, item_name, quantity, unit, expiry_date):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            INSERT INTO inventory (item_name, quantity, unit, expiry_date)
            VALUES (?, ?, ?, ?)
        """, (item_name, quantity, unit, expiry_date))
        conn.commit()
        conn.close()

    def get_inventory(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT * FROM inventory")
        inventory_items = c.fetchall()
        conn.close()

        inventory_df = pd.DataFrame(inventory_items, columns=["ID", "Item Name", "Quantity", "Unit", "Expiry Date"])
        inventory_df["Expiry Date"] = pd.to_datetime(inventory_df["Expiry Date"])
        return inventory_df

    def update_inventory(self, item_id, quantity, expiry_date):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            UPDATE inventory
            SET quantity = ?, expiry_date = ?
            WHERE id = ?
        """, (quantity, expiry_date, item_id))
        conn.commit()
        conn.close()

    def delete_item(self, item_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    def update_status(self, inventory_df):
        inventory_df["Days to Expiry"] = (inventory_df["Expiry Date"] - datetime.now()).dt.days
        inventory_df["Status"] = inventory_df["Days to Expiry"].apply(
            lambda x: "Expired" if x < 0 else ("Expiring Soon" if x <= 3 else "Good")
        )
        return inventory_df

    def display(self):
        st.subheader("📋 Manage Your Food Inventory")
        st.write("Add, view, and update your food inventory to keep track of items and avoid waste.")

        inventory_df = self.get_inventory()
        inventory_df = self.update_status(inventory_df)

        st.write("### Current Inventory")
        st.dataframe(inventory_df, use_container_width=True)

        with st.expander("Add New Item"):
            st.write("Fill out the form to add a new item:")
            with st.form("add_item_form", clear_on_submit=True):
                item_name = st.text_input("Item Name")
                quantity = st.number_input("Quantity", min_value=0.1, step=0.1, value=1.0)
                unit = st.selectbox("Unit", ["kg", "g", "unit", "L", "ml"])
                expiry_date = st.date_input("Expiry Date", value=datetime.today())
                submitted = st.form_submit_button("Add Item")

                if submitted:
                    self.add_item(item_name, quantity, unit, expiry_date)
                    st.success(f"{item_name} added to inventory!")


if __name__ == '__main__':
    auth_page = AuthPage()
    auth_page.show_auth_page()