import streamlit as st
import pandas as pd
import datetime

# --- הגדרת דף ועיצוב ---
st.set_page_config(page_title="Crypto Pro Journal", layout="wide")

# --- כותרת ---
st.title("📊 יומן מסחר קריפטו מקצועי")
st.markdown("---")

# --- ניהול הנתונים (שימוש בזיכרון זמני להדגמה) ---
if 'journal_data' not in st.session_state:
    st.session_state.journal_data = pd.DataFrame(columns=[
        'Date', 'Pair', 'Direction', 'Strategy', 'Entry Price', 'Stop Loss', 
        'Take Profit', 'Exit Price', 'Size (Units)', 'Fees ($)', 'PnL ($)', 
        'PnL (%)', 'R-Multiple', 'Rating'
    ])

# --- סרגל צד: הזנת עסקה חדשה ---
with st.sidebar:
    st.header("📝 הזנת עסקה חדשה")
    
    with st.form("trade_form", clear_on_submit=True):
        date_val = st.date_input("תאריך", datetime.date.today())
        pair = st.text_input("צמד (למשל BTC/USDT)", value="BTC/USDT").upper()
        direction = st.selectbox("כיוון", ["LONG", "SHORT"])
        strategy = st.selectbox("אסטרטגיה", ["Breakout", "Reversal", "Trend Follow", "Scalp"])
        
        col1, col2 = st.columns(2)
        with col1:
            entry_price = st.number_input("מחיר כניסה", min_value=0.0, format="%.4f")
            stop_loss = st.number_input("Stop Loss", min_value=0.0, format="%.4f")
        
        with col2:
            take_profit = st.number_input("Take Profit", min_value=0.0, format="%.4f")
            exit_price = st.number_input("מחיר יציאה בפועל", min_value=0.0, format="%.4f")
        
        size = st.number_input("גודל פוזיציה (Units)", min_value=0.0)
        fees = st.number_input("עמלות ($)", min_value=0.0)
        rating = st.slider("דירוג ביצוע (פסיכולוגיה)", 1, 5, 3)
        
        submitted = st.form_submit_button("שמור עסקה")
        
        if submitted:
            if direction == "LONG":
                pnl_usd = (exit_price - entry_price) * size - fees
                risk = entry_price - stop_loss
            else:
                pnl_usd = (entry_price - exit_price) * size - fees
                risk = stop_loss - entry_price
            
            if entry_price * size > 0:
                pnl_pct = (pnl_usd / (entry_price * size)) * 100
            else:
                pnl_pct = 0
            
            if risk > 0:
                r_multiple = pnl_usd / (risk * size)
            else:
                r_multiple = 0
            
            new_trade = {
                'Date': date_val,
                'Pair': pair,
                'Direction': direction,
                'Strategy': strategy,
                'Entry Price': entry_price,
                'Stop Loss': stop_loss,
                'Take Profit': take_profit,
                'Exit Price': exit_price,
                'Size (Units)': size,
                'Fees ($)': fees,
                'PnL ($)': round(pnl_usd, 2),
                'PnL (%)': round(pnl_pct, 2),
                'R-Multiple': round(r_multiple, 2),
                'Rating': rating
            }
            
            st.session_state.journal_data = pd.concat(
                [st.session_state.journal_data, pd.DataFrame([new_trade])], 
                ignore_index=True
            )
            st.success("העסקה נשמרה בהצלחה!")

# --- לוח בקרה (Dashboard) ---
df = st.session_state.journal_data

if not df.empty:
    total_pnl = df['PnL ($)'].sum()
    win_rate = len(df[df['PnL ($)'] > 0]) / len(df) * 100 if len(df) > 0 else 0
    avg_r = df['R-Multiple'].mean()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 רווח נקי כולל", f"${total_pnl:,.2f}")
    m2.metric("🎯 אחוז הצלחה (Win Rate)", f"{win_rate:.1f}%")
    m3.metric("⚖️ ממוצע R-Multiple", f"{avg_r:.2f}R")
    m4.metric("📝 סה״כ עסקאות", len(df))
    
    st.subheader("📈 גרף צמיחת תיק (Equity Curve)")
    df['Cumulative PnL'] = df['PnL ($)'].cumsum()
    st.line_chart(df['Cumulative PnL'])
    
    st.subheader("🗂️ היסטוריית עסקאות")
    
    def highlight_pnl(val):
        color = '#d4edda' if val > 0 else '#f8d7da'
        return f'background-color: {color}; color: black'
    
    st.dataframe(
        df.style.applymap(highlight_pnl, subset=['PnL ($)', 'PnL (%)', 'R-Multiple']),
        use_container_width=True
    )
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "הורד נתונים ל-CSV",
        data=csv,
        file_name="trading_journal.csv",
        mime="text/csv"
    )
else:
    st.info("👈 התחל להזין עסקאות בסרגל הצד כדי לראות נתונים.")
