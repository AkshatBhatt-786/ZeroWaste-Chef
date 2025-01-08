from icecream import ic
import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
import re
import os
import sys
import hashlib
import google.generativeai as genai
import requests


def get_resource_path(filepath):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath("")
    
    resource_path = os.path.join(base_path, filepath)

    if os.path.exists(resource_path):
        return resource_path
    else:
        with open(resource_path, "w") as f:
            return resource_path
    return None



DATABASE_PATH = get_resource_path("zero-waste-chef.db")

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# creating users table if not exists!
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity TEXT NOT NULL,
    unit TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    PRIMARY KEY (user_id, item_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

conn.commit()
conn.close()

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_new_user(email, password):
    is_valid_email = validate_email(email)
    if not is_valid_email:
        st.error("The email address is invalid")
        return
    is_valid_password = validate_password(password)
    if not is_valid_password:
        st.error("""
    Validates a password based on the following criteria:
    - At least 6 characters long.
    - Contains at least one lowercase letter.
    - Contains at least one uppercase letter.
    - Contains at least one symbol (non-alphanumeric character).
        """)
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute("""
        INSERT INTO users (email, password, created_at)
        VALUES (?, ?, CURRENT_TIMESTAMP);
        """, (email, hashed_password))
        conn.commit()
        st.success(f"{email} your account created successfully!")

    except sqlite3.IntegrityError as e:
        ic(f"Error: {e}")

    finally:
        conn.close()

def get_user_id(email):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def get_inventory(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT item_id, item_name, quantity, unit, expiry_date
    FROM inventory
    WHERE user_id = ?
    """, (user_id,))
    inventory = cursor.fetchall()
    conn.close()
    return inventory

def add_inventory_item(user_id, item_name, quantity, unit, expiry_date):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Calculate item_id for this user
    cursor.execute("SELECT COALESCE(MAX(item_id), 0) FROM inventory WHERE user_id = ?", (user_id,))
    item_id = cursor.fetchone()[0] + 1  # Increment item_id for the user

    # Insert the new item
    cursor.execute("""
    INSERT INTO inventory (item_id, user_id, item_name, quantity, unit, expiry_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (item_id, user_id, item_name, quantity, unit, expiry_date))
    
    conn.commit()

    if "inventory_data" in st.session_state:
        st.session_state.inventory_data = get_inventory(user_id)
    
    conn.close()
    st.rerun()

def get_recipe_suggestions(dietary_restrictions, preferred_cuisines):
    inventory = prepare_inventory_data(st.session_state.inventory_data)
    
    GEMINI_API_KEY = "AIzaSyDTnPpIk0dHdzh7e8yCMO_4-JnZV2BIsoY"
    genai.configure(api_key=GEMINI_API_KEY)
    
    prompt = (
        "You are a professional Zero-Waste Chef. Your task is to suggest recipes using the following ingredients. "
        "The goal is to utilize all ingredients efficiently before their expiry date and cater to the user's "
        "dietary restrictions and preferred cuisines. The inventory items are:\n"
        f"{', '.join(inventory)}\n"
        "The dietary restrictions are: " + ', '.join(dietary_restrictions) + ".\n"
        "The user's preferred cuisines are: " + ', '.join(preferred_cuisines) + ".\n"
        "Please suggest recipes that are practical, minimize food waste, and fit within these constraints."
    )
    
    time.sleep(4)
    # Send the request to the Gemini AI model
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
    
    # Returning the response from Gemini
    return response.text

def delete_inventory_item_by_name(user_id, item_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM inventory WHERE item_name = ? AND user_id = ?", (item_name, user_id))
    item = cursor.fetchone()
    
    if item:
        cursor.execute("DELETE FROM inventory WHERE item_name = ? AND user_id = ?", (item_name, user_id))
        conn.commit()
        st.success(f"Item '{item_name}' has been deleted successfully.")
    else:
        st.error(f"Item '{item_name}' not found in your inventory.")
    
    if "inventory_data" in st.session_state:
        st.session_state.inventory_data = get_inventory(user_id)
    
    conn.close()
    st.rerun()


def prepare_inventory_data(inventory_data):
    inventory = []
    for item in inventory_data:
        item_name = item[1]
        quantity = item[2]
        unit = item[3]
        expiry_date = item[4]
        inventory.append(f"{item_name} ({quantity} {unit}), expires on {expiry_date}")
    return inventory

def inventory_page(user_id):
    st.subheader("Inventory Management")
        
    st.markdown("### Add New Item")
    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name", key="item_name")
        quantity = st.number_input("Quantity", min_value=1.0, step=0.5, key="quantity")
        unit = st.selectbox("Unit", options=["kg", "g", "liters", "ml", "pieces", "others"], key="unit")
        expiry_date = st.date_input("Expiry Date", key="expiry_date")
        add_item_btn = st.form_submit_button("Add Item")
        if add_item_btn:
            if item_name and quantity and unit and  expiry_date:
                st.success(f"{item_name} added successfully!")
                time.sleep(3)
                add_inventory_item(user_id, item_name.strip(), quantity, unit, expiry_date.strftime("%Y-%m-%d"))
            else:
                st.warning("All fields are required!")
        
    with st.form("delete-item", clear_on_submit=True):
        inventory_names = [item[1] for item in st.session_state.inventory_data]
        # Select an item by its name to delete
        item_to_delete = st.selectbox("Select item to delete", inventory_names)
        delete_btn = st.form_submit_button("Delete Item")
        if delete_btn:
            delete_inventory_item_by_name(user_id, item_to_delete)
    # Display User's Inventory
    st.markdown("### Current Inventory")
    time.sleep(3)
    if st.session_state.inventory_data:
        df = pd.DataFrame(st.session_state.inventory_data, columns=["Item ID", "Item Name", "Quantity", "Unit", "Expiry Date"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No items in inventory yet.")

def recipe_page():
    
    st.subheader("Generate Recipie")
    inventory_data = st.session_state.inventory_data
    if not inventory_data:
        st.warning("You have no inventory items. Add some items first.")
        return

    with st.form("recipe_form", clear_on_submit=True):
        st.header("Recipe Suggestions")
        dietary_restrictions = st.multiselect(
            "Dietary Restrictions", ["Vegan", "Vegetarian", "Gluten-Free", "Dairy-Free"], key="dietary_restrictions"
        )
        preferred_cuisines = st.multiselect(
            "Preferred Cuisines", ["Italian", "Mexican", "Indian", "Chinese"], key="preferred_cuisines"
        )
        inventory = [item[1] for item in inventory_data]
        selected_items = st.multiselect(
            "Select Inventory Items", inventory, key="selected_inventory"
        )
        submit_button = st.form_submit_button("Get Recipe Suggestions")
        if submit_button:
            if not selected_items:
                st.warning("Please select at least one inventory item, preferred cuisines and dietary restriction.")
            else:
                # Call Gemini or other recipe API to get recipes based on the selected data
                recipes = get_recipe_suggestions(dietary_restrictions, preferred_cuisines)
                if recipes:
                    st.subheader("Suggested Recipes")
                    st.write("---")
                    st.write(recipes)
                else:
                    st.warning("No recipes found based on your selections.")



def redirect_to_home_page():
    if not st.session_state.get("logged_in", False):
        st.error("You are not logged in. Please log in first.")
        st.stop()

    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>ZeroWaste Chef</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #555;'>Save Food, Save Money, Save the Planet</p>",unsafe_allow_html=True)


    user_id = get_user_id(st.session_state.user_email)
    if not user_id:
        st.error("Invalid user session. Please log in again.")
        st.stop()

    if "inventory_data" not in st.session_state:
            st.session_state.inventory_data = get_inventory(user_id)
    
    selected_page = st.sidebar.radio("Go to", ["Home", "Inventory", "Suggest Recipe"])

    if selected_page == "Inventory":
        inventory_page(user_id)
        return
    if selected_page == "Suggest Recipe":
        recipe_page()
        return
    else:
        st.markdown("""
    **Welcome to ZeroWaste Chef**, your personal assistant to help you reduce food waste and manage your kitchen more efficiently. Whether you have leftovers or pantry items with approaching expiry dates, we’re here to help you save both food and money.

    Our mission is simple: **Minimize Food Waste**.
    """)

        st.markdown("""
    ### Features of ZeroWaste Chef:
    1. **Inventory Management**: Keep track of your kitchen inventory easily by adding, viewing, and removing items from your storage list. Log the name, quantity, unit, and expiry date for each item in your inventory.
    2. **Recipe Suggestions**: Based on the inventory items you already have, we'll suggest delicious recipes. No need to buy extra ingredients – use what you have!
    3. **Expiry Date Notifications**: Never worry about your food going to waste. **ZeroWaste Chef** automatically monitors the expiry dates of your stored food items and sends you timely email notifications when food is about to expire. **Get notified 1-2 days in advance**, so you can consume or repurpose items before they spoil.
        - **No More Wasting Food**: We help you stay on top of your pantry's expiration dates, reducing food waste.
        - **Get Timely Reminders**: Receive email alerts about food items nearing their expiry date, so you can use them in time.
    4. **Dietary and Cuisine Preferences**: Select dietary restrictions (e.g., Vegan, Gluten-Free) and cuisine preferences (e.g., Italian, Mexican) to get personalized recipe suggestions based on what you have in your inventory.
    5. **Sustainable Cooking**: Learn how to repurpose leftovers and make use of ingredients that are about to expire. Our goal is to make cooking easier and more sustainable for everyone.
    """)

        st.markdown("""
    ### How It Works:
    1. **Create an Account**: Sign up with your email address and create a password.
    2. **Add Your Inventory**: Log your kitchen items by adding their names, quantity, unit, and expiry date.
    3. **Get Recipe Suggestions**: Based on your inventory and preferences, get creative recipe ideas to make the most out of your food.
    4. **Set Reminders for Expiry**: Our system automatically monitors your inventory and sends you email reminders when food is about to expire.
    """)

        st.markdown("""
    ### Why ZeroWaste Chef?
    1. **Save Money**: With better inventory tracking, you’ll avoid buying unnecessary duplicates and reduce food waste.
    2. **Healthier Living**: Consume fresh, nutrient-rich ingredients while minimizing food spoilage.
    3. **Environmentally Friendly**: By reducing food waste, you are contributing to a more sustainable planet.
    """)

        st.markdown("""
    **Get Started Now and Start Saving!**
    Sign up or log in to begin managing your inventory and get recipe suggestions to create tasty dishes while reducing food waste.
    """)


        st.markdown("""
    ### Tech Stack
    - **Frontend**: Streamlit
    - **Backend**: Python, SQLite3
    """)

def validate_password(password):
    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9]).{6,}$'
    return bool(re.match(password_pattern, password))

def validate_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def authenticate_user(email, password):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, email, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if user:
        stored_password = user[2]
        if stored_password == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.user_email = user_email
            return True
        else:
            st.error("Invalid email or password.")
            return False

    conn.close()

    return False


if not st.session_state.logged_in:
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        with st.form(key="sign-in"):
        
            st.header("Login")
    
            user_email = st.text_input(label="Email")
            user_password = st.text_input(label="Password", type="password")
    
            if st.form_submit_button(label="Login", use_container_width=True):
                authenticate = authenticate_user(user_email, user_password)
                if authenticate:
                    st.rerun()
                
    
    with register_tab:
        with st.form(key="sign-up"):
        
            st.header("Register")
    
            unregistered_email = st.text_input(label="Email")
            unregistered_password = st.text_input(label="Password", type="password")
    
            register_btn = st.form_submit_button(label="Register", use_container_width=True)
            if register_btn:
                if unregistered_email and unregistered_password:
                    register_new_user(unregistered_email, unregistered_password)
                else:
                    st.warning("All fields are required!")
else:
    redirect_to_home_page()