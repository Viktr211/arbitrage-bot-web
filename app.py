# app.py
import streamlit as st
import time
import random
import sys
import os
from datetime import datetime

# Добавляем текущую папку в путь импортов (важно для Streamlit Cloud)
sys.path.insert(0, os.path.abspath('.'))

# Импорты модулей
try:
    from config import DEFAULT_ASSETS, ADMIN_EMAILS, MAIN_EXCHANGE
    from styles import get_styles
    from database import init_db, create_user, get_user, add_trade
    from exchanges import init_exchanges, get_price
    from arbitrage import find_arbitrage_opportunities
    from utils import format_trade
except ImportError as e:
    st.error(f"Ошибка импорта: {e}")
    st.stop()

# ====================== СТИЛЬ ======================
st.markdown(get_styles(), unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 НАКОПИТЕЛЬНЫЙ АРБИТРАЖ PRO v7.0</h1>', unsafe_allow_html=True)

# Инициализация базы данных
init_db()

# ====================== СЕССИЯ ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'trade_mode' not in st.session_state:
    st.session_state.trade_mode = "Демо"
if 'total_profit' not in st.session_state:
    st.session_state.total_profit = 0.0
if 'history' not in st.session_state:
    st.session_state.history = []

# Подключение бирж
exchanges = init_exchanges()

# ====================== АВТОРИЗАЦИЯ ======================
if not st.session_state.logged_in:
    tab_reg, tab_login = st.tabs(["📝 Регистрация", "🔑 Вход"])
    
    with tab_reg:
        with st.form("register_form"):
            name = st.text_input("Имя пользователя")
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            wallet = st.text_input("Адрес кошелька USDT")
            if st.form_submit_button("Зарегистрироваться"):
                if name and email and password and wallet:
                    create_user(email, password, name, wallet)
                    st.success("✅ Регистрация успешна! Теперь можно войти.")
                else:
                    st.error("❌ Заполните все поля")
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            if st.form_submit_button("Войти"):
                user = get_user(email)
                if user and user['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = user['full_name']
                    st.session_state.email = email
                    st.success(f"✅ Добро пожаловать, {st.session_state.username}!")
                    st.rerun()
                else:
                    st.error("❌ Неверный email или пароль")
    st.stop()

# ====================== ГЛАВНЫЙ ИНТЕРФЕЙС ======================
st.write(f"👤 **{st.session_state.username}**")

# Статус
status_color = "status-running" if st.session_state.bot_running else "status-stopped"
status_text = "● РАБОТАЕТ" if st.session_state.bot_running else "● ОСТАНОВЛЕН"
st.markdown(f'<div style="text-align:center;"><span class="status-dot {status_color}"></span><b>{status_text}</b></div>', unsafe_allow_html=True)

# Кнопки
c1, c2, c3 = st.columns(3)
if c1.button("▶ СТАРТ", type="primary", use_container_width=True):
    st.session_state.bot_running = True
if c2.button("⏸ ПАУЗА", use_container_width=True):
    st.session_state.bot_running = False
if c3.button("⏹ СТОП", use_container_width=True):
    st.session_state.bot_running = False

st.session_state.trade_mode = st.radio("Режим", ["Демо", "Реальный"], horizontal=True)

# Вкладки
tabs = st.tabs(["📊 Dashboard", "📈 Графики", "🔄 Арбитраж", "📦 Портфель", "💰 Кошелёк", "📜 История"])

with tabs[0]:
    st.metric("💰 Общая прибыль", f"{st.session_state.total_profit:.2f} USDT")

with tabs[2]:
    st.subheader("🔍 Арбитраж")
    if st.button("🔄 Найти возможности"):
        opps = find_arbitrage_opportunities(exchanges)
        if opps:
            for op in opps[:5]:
                st.success(f"{op['asset']} → +{op['profit_usdt']:.2f} USDT")
        else:
            st.info("Возможностей не найдено")

# Автоматический арбитраж
if st.session_state.bot_running:
    time.sleep(5)
    opps = find_arbitrage_opportunities(exchanges)
    if opps:
        best = opps[0]
        profit = best['profit_usdt']
        st.session_state.total_profit += profit
        trade_text = format_trade(best['asset'], profit, best['aux_exchange'], MAIN_EXCHANGE)
        st.session_state.history.append(trade_text)
        st.rerun()

st.caption("v7.0 — модульная версия | Если ошибка persists — напиши")
