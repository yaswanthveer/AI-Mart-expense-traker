import os
import pandas as pd
import google.generativeai as genai
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
DATA_FILE = 'expenses.csv'

def configure_genai(api_key):
    """Configures the Gemini AI client."""
    # Using hardcoded key as requested
    genai.configure(api_key="AIzaSyBapV0ZycgW6UPeMgzIFph6ZlM2MpzxfeA")
    return True

import re

def parse_expense_with_ai(user_input):
    """
    Uses Gemini AI to parse natural language expense text.
    Returns a dictionary with date, category, amount, description.
    """
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Extract the following details from the expense description: "{user_input}".
    The currency is Indian Rupee (INR/₹).
    Return a JSON object with keys: 'date' (YYYY-MM-DD, use today if not specified), 'category' (e.g., Food, Transport, Bills, Entertainment, Shopping, Other), 'amount' (float), and 'description' (short summary).
    Do not include markdown formatting like ```json. Just the raw JSON string.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up potential markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text)
    except Exception as e:
        print(f"JSON Error: {e}. Trying regex fallback.")
        # Fallback: Try to find amount (handling ₹ symbol) and use input as description
        try:
            # Matches ₹100, 100rs, 100 rupees, 100
            amount_match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(\.\d{2})?)', user_input, re.IGNORECASE)
            if amount_match:
                return {
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'category': "Other",
                    'amount': float(amount_match.group(1)),
                    'description': user_input
                }
        except:
            pass
        return None

def load_expenses():
    """Loads expenses from CSV file."""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Migration: Add Type column if missing
        if 'Type' not in df.columns:
            df['Type'] = 'Expense'
        return df
    else:
        return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description', 'Type'])

def save_expense(expense_data):
    """Saves a new expense/income to the CSV file."""
    df = load_expenses()
    new_row = pd.DataFrame([expense_data])
    # Ensure columns match
    if 'Type' not in expense_data:
        new_row['Type'] = 'Expense'
        
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return df

def get_financial_advice(df):
    """Generates financial advice based on spending habits."""
    if df.empty:
        return "Start adding expenses to get AI-powered advice!"
    
    # Filter for expenses only for advice
    expenses = df[df['Type'] == 'Expense']
    if expenses.empty:
        return "Great job! No expenses recorded yet."

    summary = expenses.groupby('Category')['Amount'].sum().to_dict()
    total_spent = expenses['Amount'].sum()
    
    prompt = f"""
    Analyze these spending habits (in Indian Rupees ₹): {summary}. Total spent: ₹{total_spent}.
    Give a short, friendly financial tip (max 2 sentences) relevant to an Indian context if applicable.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Keep tracking your expenses to save more!"

def get_shopping_advice(item_description, amount):
    """
    Asks the user how they felt and gives discount tips.
    """
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    The user just spent ₹{amount} on "{item_description}".
    1. Ask them a short, engaging question about how they feel about this purchase (e.g., "Was it worth it?", "Do you love it?").
    2. Give a quick tip on how to get a discount or save money on this kind of item next time (mention Indian platforms like Amazon/Flipkart/Swiggy/Zomato if relevant).
    Keep it brief (max 3 sentences total).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Hope it was a good purchase! Check for coupons next time."
