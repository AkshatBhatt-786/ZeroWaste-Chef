# ZeroWaste Chef

**ZeroWaste Chef** is a hackathon project aimed at helping users reduce food waste by efficiently managing their kitchen inventory and suggesting recipes using available ingredients before they expire. The platform enables users to log their kitchen items, track expiry dates, and receive personalized recipe suggestions based on dietary preferences and available ingredients.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)

## Introduction

ZeroWaste Chef is designed to help minimize food waste, save money, and make cooking more sustainable. By automatically notifying users when their food items are nearing expiry, it helps them consume ingredients in time or repurpose leftovers. With recipe suggestions based on available inventory, users can easily reduce waste and create healthy meals without unnecessary shopping.

### Key Features:
- **Inventory Management**: Track your kitchen inventory by logging items, their quantities, units, and expiry dates.
- **Recipe Suggestions**: Get recipe suggestions based on the items you already have in your kitchen.
- **Expiry Date Notifications**: Receive notifications via email when items are approaching their expiry date.
- **Dietary & Cuisine Preferences**: Customize your meal suggestions based on dietary preferences (e.g., Vegan, Gluten-Free) and preferred cuisines (e.g., Italian, Mexican).
- **Sustainable Cooking**: Learn how to repurpose leftover ingredients and minimize food waste.

## Features

1. **Inventory Management**: 
   - Add new items to your inventory.
   - View your current kitchen stock.
   - Remove items once they are used or expired.

2. **Recipe Suggestions**: 
   - Based on your inventory, dietary restrictions, and cuisine preferences, we suggest recipes to help you use up your ingredients.

3. **Expiry Date Reminders**: 
   - Stay informed about the expiry of food items with timely email notifications.

4. **Customizable Preferences**: 
   - Select your dietary restrictions and preferred cuisines to get more relevant recipe suggestions.

5. **Sustainability Focus**: 
   - Reduce food waste and save money by utilizing ingredients that are about to expire.

## How It Works

1. **Create an Account**: 
   - Sign up with your email and password.
   
2. **Log Inventory**: 
   - Add food items to your kitchen inventory by entering the name, quantity, unit, and expiry date of each item.
   
3. **Get Recipe Suggestions**: 
   - Based on the inventory items and your dietary restrictions, receive recipe ideas that minimize waste and use up ingredients effectively.

4. **Expiry Date Notifications**: 
   - The system will notify you when your food items are about to expire, allowing you to use them before they go bad.

5. **Sustainable Cooking**: 
   - Use the leftover ingredients efficiently and repurpose them for new meals.

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python, SQLite3
- **Database**: SQLite (for storing user data and inventory)
- **Generative AI**: Google Gemini API (for generating recipe suggestions based on inventory and preferences)
- **Email Notifications**: SMTP (for sending expiry reminders)
- **Version Control**: Git & GitHub

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.x
- Streamlit
- SQLite3
- Required Python libraries (requrirements.txt)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AkshatBhatt-786/ZeroWaste-Chef.git
   cd ZeroWaste-Chef

2. pip install -r requirements.txt

3. streamlit run app.py

4. Follow the on-screen instructions to register, log in, and start managing your inventory.