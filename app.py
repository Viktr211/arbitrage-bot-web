# app.py
import streamlit as st
import time
import random
from datetime import datetime

from config import DEFAULT_ASSETS, ADMIN_EMAILS
from styles import get_styles
from database import init_db, create_user, get_user, add_trade
from exchanges import init_exchanges, get_price
from arbitrage import find_arbitrage_opportunities
from utils import format_trade

st.markdown(get_styles(), unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🚀 НАКОПИТЕЛЬНЫЙ АРБИТРАЖ PRO v7.0</h1>', unsafe_allow_html=True)

init_db()

# Инициализация сессии
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'trade_mode' not in st.session_state:
    st.session_state.trade_mode = "Демо"
if 'history' not in st.session_state:
    st.session_state.history = []
if 'total_profit' not in st.session_state:
    st.session_state.total_profit = 0.0

exchanges = init_exchanges()

# ====================== АВТОРИЗАЦИЯ ======================
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Регистрация", "Вход"])
    with tab1:
        with st.form("reg"):
            name = st.text_input("Имя")
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            wallet = st.text_input("Адрес кошелька USDT")
            if st.form_submit_button("Зарегистрироваться"):
                create_user(email, password, name, wallet)
                st.success("Регистрация прошла успешно!")
    with tab2:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            if st.form_submit_button("Войти"):
                user = get_user(email)
                if user and user['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = user['full_name']
                    st.session_state.email = email
                    st.rerun()
    st.stop()

# ====================== ОСНОВНОЙ ИНТЕРФЕЙС ======================
st.write(f"👤 {st.session_state.username} | Баланс: 10,000 USDT")

col1, col2, col3 = st.columns([1,1,1])
if col1.button("▶ СТАРТ", type="primary"):
    st.session_state.bot_running = True
if col2.button("⏸ ПАУЗА"):
    st.session_state.bot_running = False
if col3.button("⏹ СТОП"):
    st.session_state.bot_running = False

st.session_state.trade_mode = st.radio("Режим", ["Демо", "Реальный"], horizontal=True)

tabs = st.tabs(["Dashboard", "Графики", "Арбитраж", "Портфель", "Кошелёк", "История"])

with tabs[0]:
    st.metric("Общая прибыль", f"{st.session_state.total_profit:.2f} USDT")

with tabs[2]:
    if st.button("🔍 Найти арбитраж"):
        opps = find_arbitrage_opportunities(exchanges)
        if opps:
            for op in opps[:5]:
                st.success(f"{op['asset']} → +{op['profit_usdt']:.2f} USDT")
        else:
            st.info("Возможностей не найдено")

# Авто-арбитраж
if st.session_state.bot_running:
    time.sleep(5)
    opps = find_arbitrage_opportunities(exchanges)
    if opps:
        best = opps[0]
        profit = best['profit_usdt']
        st.session_state.total_profit += profit
        st.session_state.history.append(format_trade(best['asset'], profit, best['aux_exchange'], MAIN_EXCHANGE))
        add_trade(1, best['asset'], profit, best['aux_exchange'], MAIN_EXCHANGE)  # user_id=1 для теста
        st.rerun()

st.caption("Накопительный Арбитраж PRO v7.0 — модульная структура")
