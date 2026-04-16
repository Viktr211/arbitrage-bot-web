# app.py
import streamlit as st
import time
import random
import sys
import os
from datetime import datetime

# Исправление импортов для Streamlit Cloud
sys.path.insert(0, os.path.abspath('.'))

from config import DEFAULT_ASSETS, ADMIN_EMAILS
from styles import get_styles
from database import init_db, create_user, get_user, add_trade
from exchanges import init_exchanges, get_price
from arbitrage import find_arbitrage_opportunities
from utils import format_trade

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
    st.markdown('<h1 class="main-header">🚀 НАКОПИТЕЛЬНЫЙ АРБИТРАЖ PRO v7.0</h1>', unsafe_allow_html=True)
    
    tab_reg, tab_login = st.tabs(["📝 Регистрация", "🔑 Вход"])
    
    with tab_reg:
        with st.form("register_form"):
            name = st.text_input("Имя пользователя")
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            wallet = st.text_input("Адрес кошелька USDT (TRC20)")
            submitted = st.form_submit_button("Зарегистрироваться")
            if submitted:
                if name and email and password and wallet:
                    create_user(email, password, name, wallet)
                    st.success("✅ Регистрация успешна! Теперь можно войти.")
                else:
                    st.error("❌ Заполните все поля")
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            submitted = st.form_submit_button("Войти")
            if submitted:
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

# ====================== ОСНОВНОЙ ИНТЕРФЕЙС ======================
st.write(f"👤 **{st.session_state.username}** | Баланс: **10,000 USDT**")

# Статус бота
status_color = "status-running" if st.session_state.bot_running else "status-stopped"
status_text = "● РАБОТАЕТ 24/7" if st.session_state.bot_running else "● ОСТАНОВЛЕН"
st.markdown(f'<div style="text-align:center; font-size:18px;"><span class="status-dot {status_color}"></span><b>{status_text}</b></div>', unsafe_allow_html=True)

# Кнопки управления
c1, c2, c3 = st.columns(3)
if c1.button("▶ СТАРТ", type="primary", use_container_width=True):
    st.session_state.bot_running = True
if c2.button("⏸ ПАУЗА", use_container_width=True):
    st.session_state.bot_running = False
if c3.button("⏹ СТОП", use_container_width=True):
    st.session_state.bot_running = False

st.session_state.trade_mode = st.radio("Режим работы", ["Демо", "Реальный"], horizontal=True)

# Вкладки
tabs = st.tabs(["📊 Dashboard", "📈 Графики", "🔄 Арбитраж", "📦 Портфель", "💰 Кошелёк", "📜 История"])

with tabs[0]:
    st.subheader("📊 Общая статистика")
    st.metric("💰 Общая прибыль", f"{st.session_state.total_profit:.2f} USDT")
    st.metric("📊 Всего сделок", len(st.session_state.history))

with tabs[1]:
    st.subheader("📈 Японские свечи")
    asset = st.selectbox("Выберите токен", DEFAULT_ASSETS)
    st.info("График будет добавлен в следующей версии")

with tabs[2]:
    st.subheader("🔍 Арбитражные возможности")
    if st.button("🔄 Найти возможности", use_container_width=True):
        opportunities = find_arbitrage_opportunities(exchanges)
        if opportunities:
            st.success(f"Найдено {len(opportunities)} возможностей!")
            for op in opportunities[:8]:
                st.info(f"🎯 **{op['asset']}** | OKX ${op['main_price']:.2f} → {op['aux_exchange'].upper()} ${op['aux_price']:.2f} | +{op['profit_usdt']:.2f} USDT")
        else:
            st.info("Пока нет выгодных спредов")

with tabs[3]:
    st.subheader("📦 Портфель (OKX)")
    total_value = 0
    for asset in DEFAULT_ASSETS:
        amount = 0.0
        price = get_price(exchanges.get(MAIN_EXCHANGE), asset) if exchanges else None
        if price:
            value = amount * price
            total_value += value
            st.write(f"**{asset}**: {amount:.6f} ≈ ${value:,.2f}")
    st.metric("Общая стоимость портфеля", f"${total_value:,.2f}")

with tabs[4]:
    st.subheader("💰 Кошелёк")
    st.metric("Баланс USDT", "10,000.00")
    st.text_input("Адрес для вывода (TRC20)", value="")
    if st.button("Запросить вывод"):
        st.success("Заявка на вывод отправлена!")

with tabs[5]:
    st.subheader("📜 История сделок")
    if st.session_state.history:
        for trade in reversed(st.session_state.history[-30:]):
            st.write(trade)
        if st.button("Очистить историю"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("История пока пуста")

# ====================== ОСНОВНОЙ ЦИКЛ АРБИТРАЖА ======================
if st.session_state.bot_running:
    time.sleep(6)
    opportunities = find_arbitrage_opportunities(exchanges)
    
    if opportunities:
        best = opportunities[0]
        profit = best['profit_usdt']
        
        st.session_state.total_profit += profit
        trade_text = format_trade(best['asset'], profit, best['aux_exchange'], MAIN_EXCHANGE)
        st.session_state.history.append(trade_text)
        
        st.toast(f"🎯 {best['asset']} | +{profit:.2f} USDT", icon="💰")
        st.rerun()

st.caption("Накопительный Арбитраж PRO v7.0 — модульная версия")
