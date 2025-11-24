@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting AI Expense Tracker...
streamlit run app.py
pause
