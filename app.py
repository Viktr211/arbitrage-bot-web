import streamlit as st
import time
import random
from datetime import datetime

st.set_page_config(page_title="Накопительный Арбитраж PRO v7.0", layout="wide", page_icon="🚀")

# ====================== СТИЛЬ ======================
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #001a33 0%, #003087 100%); color: white; }
    .main-header { font-size: 32px; font-weight: bold; color: #00D4FF; text-align: center; margin-bottom: 10px; }
    .status-dot { display: inline-block; width: 16px; height: 16px; border-radius: 50%; margin-right: 8px; }
    .status-running { background-color: #00FF88; box-shadow: 0 0 12px #00FF88; animation: pulse 2s infinite; }
    .status-stopped { background-color: #FF4444; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 НАКОПИТЕЛЬНЫЙ АРБИТРАЖ PRO v7.0</h1>', unsafe_allow_html=True)

# ====================== КОНФИГУРАЦИЯ ======================
DEFAULT_ASSETS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "LINK", "SUI", "HYPE"]
MAIN_EXCHANGE = "okx"
AUX_EXCHANGES = ["kucoin", "gateio", "bitget", "bingx", "mexc"]

MIN_SPREAD_PERCENT = 0.35

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

# ====================== АВТОРИЗАЦИЯ ======================
if not st.session_state.logged_in:
    tab_reg, tab_login = st.tabs(["📝 Регистрация", "🔑 Вход"])
    
    with tab_reg:
        with st.form("reg_form"):
            name = st.text_input("Имя пользователя")
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            if st.form_submit_button("Зарегистрироваться"):
                if name and email and password:
                    st.session_state.logged_in = True
                    st.session_state.username = name
                    st.session_state.email = email
                    st.success("✅ Регистрация успешна!")
                    st.rerun()
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            if st.form_submit_button("Войти"):
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.username = email.split('@')[0]
                    st.session_state.email = email
                    st.success(f"✅ Добро пожаловать!")
                    st.rerun()
    st.stop()

# ====================== ГЛАВНЫЙ ИНТЕРФЕЙС ======================
st.write(f"👤 **{st.session_state.username}**")

# Статус
status_color = "status-running" if st.session_state.bot_running else "status-stopped"
status_text = "● РАБОТАЕТ 24/7" if st.session_state.bot_running else "● ОСТАНОВЛЕН"
st.markdown(f'<div style="text-align:center; font-size:18px;"><span class="status-dot {status_color}"></span><b>{status_text}</b></div>', unsafe_allow_html=True)

# Кнопки
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
    st.metric("💰 Общая прибыль", f"{st.session_state.total_profit:.2f} USDT")

with tabs[2]:
    st.subheader("🔍 Арбитраж")
    if st.button("🔄 Найти арбитражные возможности"):
        st.info("Поиск спреда между OKX и другими биржами...")
        # Симуляция
        st.success("Найдено 3 возможности!")
        st.info("🎯 HYPE → +5.42 USDT")
        st.info("🎯 SOL  → +3.18 USDT")

with tabs[3]:
    st.subheader("📦 Портфель на OKX")
    for asset in DEFAULT_ASSETS:
        st.write(f"**{asset}**: {random.uniform(0.1, 100):.4f}")
    st.metric("Общая стоимость", "$10,245.67")

with tabs[5]:
    st.subheader("📜 История сделок")
    if st.session_state.history:
        for trade in reversed(st.session_state.history[-20:]):
            st.write(trade)
    else:
        st.info("Пока нет сделок")

# ====================== ОСНОВНОЙ ЦИКЛ ======================
if st.session_state.bot_running:
    time.sleep(5)
    asset = random.choice(DEFAULT_ASSETS)
    profit = round(random.uniform(1.5, 7.5), 2)
    
    st.session_state.total_profit += profit
    trade_text = f"✅ {datetime.now().strftime('%H:%M:%S')} | {asset} | +{profit:.2f} USDT"
    st.session_state.history.append(trade_text)
    
    st.toast(f"🎯 Сделка по {asset} | +{profit} USDT", icon="💰")
    st.rerun()

st.caption("Накопительный Арбитраж PRO v7.0 — всё в одном файле")
