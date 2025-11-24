# 💸 AI Smart Expense Tracker

A premium, Apple-style expense tracker powered by Google Gemini AI.

## Features
- **Natural Language Entry**: Just type "Spent $15 on lunch" and AI handles the rest.
- **Dual Modes**:
    - **Gen Z Mode 🤟**: Fun, emoji-rich interface with vibe checks.
    - **Employee Mode 💼**: Professional dashboard with detailed tables and CSV export.
- **Smart Insights**: AI-powered financial advice based on your spending.
- **Data Persistence**: Saves all your expenses to `expenses.csv`.

## Setup
1.  **Install Python** (if not already installed).
2.  **Get a Gemini API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey).
3.  **Run the App**:
    - Double-click `run_app.bat`.
    - OR run in terminal: `streamlit run app.py`.

## Configuration
You can enter your API key in the sidebar every time, OR create a `.env` file in this folder:
```
GOOGLE_API_KEY=your_actual_api_key_here
```
The app will automatically load it.
