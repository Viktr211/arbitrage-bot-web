import streamlit as st
import time
import random
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Накопительный Арбитраж PRO v7.1-fix", layout="wide", page_icon="🚀")

# ====================== СТИЛЬ ======================
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #001a33 0%, #003087 100%); color: white; }
    .main-header { font-size: 32px; font-weight: bold; color: #00D4FF; text-align: center; }
    .status-dot { display: inline-block; width: 16px; height: 16px; border-radius: 50%; margin-right: 8px; }
    .status-running { background-color: #00FF88; box-shadow: 0 0 12px #00FF88; animation: pulse 2s infinite; }
    .status-stopped { background-color: #FF4444; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 НАКОПИТЕЛЬНЫЙ АРБИТРАЖ PRO v7.1-fix</h1>', unsafe_allow_html=True)

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
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False

# ====================== АВТОРИЗАЦИЯ ======================
if not st.session_state.logged_in:
    tab_reg, tab_login = st.tabs(["📝 Регистрация", "🔑 Вход"])
    
    with tab_reg:
        with st.form("reg_form"):
            full_name = st.text_input("ФИО")
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            wallet = st.text_input("Адрес кошелька USDT")
            if st.form_submit_button("Зарегистрироваться"):
                if full_name and email and password:
                    conn = get_db()
                    conn.execute("""
                        INSERT INTO users (email, password, full_name, wallet_address, created_at, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (email, password, full_name, wallet, datetime.now().strftime("%Y-%m-%d %H:%M"), 'pending'))
                    conn.commit()
                    conn.close()
                    st.success("✅ Заявка отправлена на одобрение администратору!")
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            if st.form_submit_button("Войти"):
                conn = get_db()
                user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
                conn.close()
                
                if user:
                    # Специальное правило для админа
                    if email == "cb777899@gmail.com":
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.username = user['full_name'] or "Администратор"
                        st.session_state.user_id = user['id']
                        st.success("✅ Вход как Администратор выполнен!")
                        st.rerun()
                    elif user['status'] == 'approved':
                        st.session_state.logged_in = True
                        st.session_state.is_admin = False
                        st.session_state.username = user['full_name']
                        st.session_state.user_id = user['id']
                        st.success(f"✅ Добро пожаловать, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.warning("⏳ Ваша заявка ещё не одобрена администратором.")
                else:
                    st.error("❌ Неверный email или пароль")
    st.stop()

# ====================== ГЛАВНЫЙ ИНТЕРФЕЙС ======================
st.write(f"👤 **{st.session_state.username}**")

if st.session_state.is_admin:
    st.success("👑 Вы вошли как Администратор")

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

# Вкладки
if st.session_state.is_admin:
    tabs = st.tabs(["📊 Dashboard", "🔄 Арбитраж", "👥 Пользователи", "💰 Заявки на вывод", "📜 История"])
else:
    tabs = st.tabs(["📊 Dashboard", "🔄 Арбитраж", "📦 Портфель", "💰 Кошелёк", "📜 История"])

with tabs[0]:
    st.metric("💰 Общая прибыль", "0.00 USDT")

with tabs[1]:
    st.subheader("🔄 Арбитраж")
    if st.button("🔄 Найти возможности"):
        st.info("Поиск спреда между биржами...")
        st.success("Найдено 2 арбитражные возможности")

# Админ-панель — Пользователи
if st.session_state.is_admin:
    with tabs[2]:
        st.subheader("👥 Управление пользователями")
        conn = get_db()
        users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
        conn.close()
        
        for user in users:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{user['full_name']}** — {user['email']} | Статус: **{user['status']}**")
            with col2:
                if user['status'] == 'pending':
                    if st.button("✅ Одобрить", key=f"app_{user['id']}"):
                        conn = get_db()
                        conn.execute("UPDATE users SET status = 'approved' WHERE id = ?", (user['id'],))
                        conn.commit()
                        conn.close()
                        st.success(f"Пользователь {user['email']} одобрен!")
                        st.rerun()
            with col3:
                if user['status'] == 'pending':
                    if st.button("❌ Отклонить", key=f"rej_{user['id']}"):
                        conn = get_db()
                        conn.execute("UPDATE users SET status = 'rejected' WHERE id = ?", (user['id'],))
                        conn.commit()
                        conn.close()
                        st.warning(f"Пользователь {user['email']} отклонён!")
                        st.rerun()

# Заявки на вывод (для админа)
if st.session_state.is_admin:
    with tabs[3]:
        st.subheader("💰 Заявки на вывод средств")
        st.info("Выводы обрабатываются по **вторникам и пятницам**.")

# История
with tabs[-1]:
    st.subheader("📜 История сделок")
    st.info("Здесь будет отображаться история арбитражных сделок")

# Симуляция работы бота
if st.session_state.bot_running:
    time.sleep(6)
    profit = round(random.uniform(1.8, 6.5), 2)
    st.toast(f"🎯 Арбитраж выполнен! +{profit} USDT", icon="💰")
    st.rerun()

st.caption("v7.1-fix — Админ входит без одобрения | Остальные пользователи — с одобрением")
