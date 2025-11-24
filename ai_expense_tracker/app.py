import streamlit as st
import os
import pandas as pd
import plotly.express as px
from utils import configure_genai, parse_expense_with_ai, save_expense, load_expenses, get_financial_advice, get_shopping_advice

# Page Config
st.set_page_config(page_title="AI Smart Expense Tracker", page_icon="💸", layout="wide")

# Load CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    # Try to get key from environment
    default_key = os.getenv("GOOGLE_API_KEY", "")
    api_key = st.text_input("Gemini API Key", value=default_key, type="password", help="Get your key from Google AI Studio")
    
    st.divider()
    
    mode = st.radio("Select Mode", ["Visual Mode 🎨", "Employee 💼"])
    
    st.divider()
    if st.button("Reset All Data 🗑️"):
        if os.path.exists("expenses.csv"):
            os.remove("expenses.csv")
            st.rerun()
    
    st.divider()
    st.markdown("### About")
    st.caption("Powered by Gemini AI & Streamlit")

# Initialize AI
ai_configured = configure_genai(api_key)

# Main Layout
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Header
    if mode == "Visual Mode 🎨":
        st.markdown('<h1>Check Your Wallet</h1>', unsafe_allow_html=True)
        st.caption("Track your money, see your balance.")
    else:
        st.markdown('<h1>💼 Professional Expense Tracker</h1>', unsafe_allow_html=True)
        st.caption("Efficiently manage and analyze your corporate or personal spending.")

    # Balance Section
    df = load_expenses()
    total_income = df[df['Type'] == 'Income']['Amount'].sum() if not df.empty else 0
    total_expense = df[df['Type'] == 'Expense']['Amount'].sum() if not df.empty else 0
    balance = total_income - total_expense

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<p style="margin-bottom: 0;">Current Balance</p><div class="balance-text">₹{balance:,.2f}</div>', unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns(2)
    b_col1.caption(f"Total Income: +₹{total_income:,.2f}")
    b_col2.caption(f"Total Expenses: -₹{total_expense:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Transaction Input Section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    tab_expense, tab_income = st.tabs(["Add Expense 💸", "Add Income 💰"])
    
    with tab_expense:
        st.subheader("New Expense")
        
        exp_type = st.radio("Entry Method", ["✨ AI Assistant", "📝 Manual Entry"], horizontal=True, label_visibility="collapsed")
        
        if exp_type == "✨ AI Assistant":
            if not ai_configured:
                st.warning("Please enter your Gemini API Key in the sidebar to use AI features.")
                expense_input = st.text_input("Describe your expense (AI disabled)", disabled=True)
            else:
                expense_input = st.text_input("Tell me what you spent...", placeholder="e.g., Spent ₹250 on burgers")
                
                if st.button("Add Expense (AI)"):
                    if expense_input:
                        with st.spinner("Processing..."):
                            parsed_data = parse_expense_with_ai(expense_input)
                            if parsed_data:
                                formatted_data = {
                                    'Date': parsed_data.get('date'),
                                    'Category': parsed_data.get('category'),
                                    'Amount': parsed_data.get('amount'),
                                    'Description': parsed_data.get('description'),
                                    'Type': 'Expense'
                                }
                                save_expense(formatted_data)
                                st.success(f"Added Expense: {formatted_data['Description']} - ₹{formatted_data['Amount']}")
                                
                                # AI Advice
                                advice = get_shopping_advice(formatted_data['Description'], formatted_data['Amount'])
                                st.info(f"🤖 AI says: {advice}")
                                
                            else:
                                st.error("Could not parse expense. Please try again.")
        
        else: # Manual Entry
            with st.form("manual_expense_form"):
                col_desc, col_amt = st.columns([2, 1])
                m_desc = col_desc.text_input("Description", placeholder="e.g. Coffee")
                m_amount = col_amt.number_input("Amount (₹)", min_value=0.0, step=1.0)
                
                col_cat, col_date = st.columns(2)
                m_category = col_cat.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"])
                m_date = col_date.date_input("Date", value=pd.Timestamp.now())
                
                if st.form_submit_button("Add Expense"):
                    if m_desc and m_amount > 0:
                        manual_data = {
                            'Date': m_date.strftime("%Y-%m-%d"),
                            'Category': m_category,
                            'Amount': m_amount,
                            'Description': m_desc,
                            'Type': 'Expense'
                        }
                        save_expense(manual_data)
                        st.success(f"Added: {m_desc} - ₹{m_amount}")
                        
                        if ai_configured:
                             # AI Advice for manual too
                            advice = get_shopping_advice(m_desc, m_amount)
                            st.info(f"🤖 AI says: {advice}")

    with tab_income:
        st.subheader("New Income")
        income_desc = st.text_input("Source", placeholder="e.g., Salary, Freelance")
        income_amount = st.number_input("Amount", min_value=0.0, step=10.0)
        
        if st.button("Add Income"):
            if income_desc and income_amount > 0:
                income_data = {
                    'Date': pd.Timestamp.now().strftime("%Y-%m-%d"),
                    'Category': 'Income',
                    'Amount': income_amount,
                    'Description': income_desc,
                    'Type': 'Income'
                }
                save_expense(income_data)
                st.success(f"Added Income: {income_desc} - ₹{income_amount}")
                st.balloons()

    st.markdown('</div>', unsafe_allow_html=True)

    # Dashboard Section
    # Reload df to get latest data
    df = load_expenses()
    
    if not df.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Spending Overview")
        
        if ai_configured:
            advice = get_financial_advice(df)
            st.info(f"💡 Financial Tip: {advice}")
        
        # Filter for expenses only for charts
        expenses_df = df[df['Type'] == 'Expense']
        
        if not expenses_df.empty:
            if mode == "Visual Mode 🎨":
                st.markdown("### 🎨 Where's the money going?")
                # Dark Mode Pie Chart
                fig = px.pie(expenses_df, values='Amount', names='Category', hole=0.4, 
                             color_discrete_sequence=['#ffffff', '#cccccc', '#999999', '#666666', '#333333'])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#ffffff"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("See the receipts (Data)"):
                    st.dataframe(df, use_container_width=True)
                    
            else: # Employee Mode
                st.markdown("### 📊 Detailed Analysis")
                
                tab1, tab2 = st.tabs(["Charts", "Raw Data"])
                
                with tab1:
                    # Dark Mode Bar Chart
                    fig = px.bar(expenses_df, x='Category', y='Amount', title="Expenses by Category")
                    fig.update_traces(marker_color='#ffffff')
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#ffffff",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    st.dataframe(df, use_container_width=True)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Report (CSV)", csv, "expenses.csv", "text/csv")
        else:
            st.info("No expenses yet. You're saving 100% of your income! 🤑")
                
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No transactions recorded yet. Add one above!")

