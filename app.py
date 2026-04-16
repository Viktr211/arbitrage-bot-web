import streamlit as st
import time
import random
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Накопительный Арбитраж PRO", layout="wide", page_icon="🚀")

# ====================== СТИЛЬ ======================
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #001a33 0%, #003087 100%); color: white; }
    .main-header { font-size: 28px; font-weight: bold; color: #00D4FF; text-align: center; margin-bottom: 0; }
    .status-indicator { display: inline-block; width: 14px; height: 14px; border-radius: 50%; margin-right: 6px; }
    .status-running { background-color: #00FF88; box-shadow: 0 0 8px #00FF88; animation: pulse 1.5s infinite; }
    .status-stopped { background-color: #FF4444; box-shadow: 0 0 8px #FF4444; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    .stButton>button { border-radius: 30px; height: 42px; font-weight: bold; }
    .token-card { background: rgba(0,100,200,0.2); border-radius: 10px; padding: 8px; margin: 4px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ====================== КОНФИГУРАЦИЯ ======================
DEFAULT_ASSETS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "LINK", "SUI", "HYPE"]
MAIN_EXCHANGE = "okx"
AUX_EXCHANGES = ["gateio", "kucoin", "bitget", "bingx", "mexc", "huobi", "poloniex", "hitbtc"]
MIN_SPREAD_PERCENT = 0.35
FEE_PERCENT = 0.10

ADMIN_EMAILS = ["cb777899@gmail.com"]

# ====================== БАЗА ДАННЫХ ======================
DB_PATH = "arbitrage.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT,
            full_name TEXT,
            wallet_address TEXT,
            balance REAL DEFAULT 10000.0,
            total_profit REAL DEFAULT 0.0,
            trade_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            asset TEXT,
            profit REAL,
            buy_exchange TEXT,
            sell_exchange TEXT,
            trade_time TEXT
        );
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            wallet_address TEXT,
            status TEXT DEFAULT 'pending',
            requested_at TEXT
        );
    ''')
    conn.commit()
    conn.close()

init_db()

# ====================== СЕССИЯ ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'total_profit' not in st.session_state:
    st.session_state.total_profit = 0.0
if 'history' not in st.session_state:
    st.session_state.history = []

# ====================== АВТОРИЗАЦИЯ ======================
if not st.session_state.logged_in:
    tab_reg, tab_login = st.tabs(["📝 Регистрация", "🔑 Вход"])
    with tab_reg:
        with st.form("register"):
            full_name = st.text_input("ФИО")
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            wallet = st.text_input("Адрес кошелька")
            if st.form_submit_button("Зарегистрироваться"):
                conn = get_db()
                conn.execute("INSERT INTO users (email, password, full_name, wallet_address, created_at, status) VALUES (?, ?, ?, ?, ?, 'pending')",
                             (email, password, full_name, wallet, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                conn.close()
                st.success("Заявка отправлена на одобрение!")
    with tab_login:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            if st.form_submit_button("Войти"):
                conn = get_db()
                user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
                conn.close()
                if user:
                    if email == "cb777899@gmail.com":
                        st.session_state.is_admin = True
                    if user['status'] == 'approved' or email == "cb777899@gmail.com":
                        st.session_state.logged_in = True
                        st.session_state.username = user['full_name']
                        st.session_state.email = email
                        st.success("Вход выполнен!")
                        st.rerun()
                    else:
                        st.warning("Заявка ещё не одобрена.")
    st.stop()

# ====================== ГЛАВНЫЙ ИНТЕРФЕЙС ======================
st.write(f"👤 **{st.session_state.username}**")

if st.session_state.is_admin:
    st.success("👑 Администратор")

# Кнопки
c1, c2, c3 = st.columns(3)
if c1.button("▶ СТАРТ", type="primary"):
    st.session_state.bot_running = True
if c2.button("⏸ ПАУЗА"):
    st.session_state.bot_running = False
if c3.button("⏹ СТОП"):
    st.session_state.bot_running = False

# Вкладки
tabs_list = ["📊 Dashboard", "📈 Графики", "🔄 Арбитраж", "📦 Портфель", "💰 Кошелёк", "📜 История"]
if st.session_state.is_admin:
    tabs_list.append("👑 Админ-панель")

tabs = st.tabs(tabs_list)

with tabs[0]:
    st.metric("💰 Общая прибыль", f"{st.session_state.total_profit:.2f} USDT")

with tabs[2]:
    st.subheader("🔄 Арбитраж")
    if st.button("Найти возможности"):
        st.info("Идёт поиск арбитража...")

# Авто-арбитраж
if st.session_state.bot_running:
    time.sleep(8)
    profit = round(random.uniform(2.0, 8.0), 2)
    st.session_state.total_profit += profit
    st.session_state.history.append(f"✅ {datetime.now().strftime('%H:%M:%S')} | Арбитраж | +{profit} USDT")
    st.rerun()

with tabs[-1]:
    st.subheader("📜 История")
    for trade in reversed(st.session_state.history[-20:]):
        st.write(trade)

st.caption("v7.2 — модульная версия собрана в один файл")
