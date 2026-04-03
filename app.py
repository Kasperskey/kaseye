import streamlit as st
import pandas as pd
import requests
from PIL import Image
import io
import urllib.parse
import json

# --- КОНФИГУРАЦИЯ ТЕРМИНАЛА ---
st.set_page_config(page_title="KASEYE Elite v5.0", layout="wide", page_icon="⚡")

# --- ФУНКЦИЯ LIVE-АНАЛИЗА НОМЕРА ---
def get_phone_info(phone_num):
    try:
        # Запрос к открытому API для определения ГЕО и Оператора
        response = requests.get(f"https://htmlweb.ru/geo/api.php?json&tel={phone_num}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- ГЛОБАЛЬНЫЙ КИБЕР-ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e0e6ed; font-family: 'Consolas', monospace; }
    [data-testid="stSidebar"] { background-color: rgba(10, 13, 18, 0.95) !important; border-right: 2px solid #1a202c; }
    .sidebar-title {
        color: #58a6ff; font-size: 26px; font-weight: 800; text-shadow: 0 0 15px rgba(88, 166, 255, 0.5);
        text-align: center; margin-bottom: 10px; letter-spacing: 3px;
    }
    .stButton>button { 
        width: 100%; background-image: linear-gradient(135deg, #d73a49 0%, #a71a26 100%);
        color: white; border-radius: 4px; font-weight: bold; border: 1px solid #ff7b72; 
        height: 3.5em; text-transform: uppercase; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(215, 58, 73, 0.8); transform: translateY(-2px); }
    h1, h2, h3 { color: #58a6ff; text-shadow: 0 0 10px rgba(88, 166, 255, 0.4); }
    .data-card {
        background-color: rgba(16, 20, 27, 0.9); border: 1px solid #30363d;
        border-radius: 8px; padding: 15px; margin-bottom: 10px; transition: 0.3s;
        border-left: 4px solid #58a6ff;
    }
    .live-box {
        background: rgba(46, 160, 67, 0.1); border: 1px solid #2ea043;
        padding: 15px; border-radius: 8px; margin-bottom: 20px;
    }
    .card-link { color: #58a6ff !important; text-decoration: none; font-size: 1em; font-weight: bold; }
    .card-link:hover { text-shadow: 0 0 10px #58a6ff; text-decoration: underline; }
    .online-indicator { color: #2ea043; font-weight: bold; animation: pulse 2.5s infinite; text-align: center; font-size: 0.8em; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>KASEYE</div>", unsafe_allow_html=True)
    st.markdown("<p class='online-indicator'>● SYSTEM STATUS: ACTIVE</p>", unsafe_allow_html=True)
    st.divider()

    menu = st.radio("ВЕКТОРЫ РАЗВЕДКИ:", [
        "📞 Телефон (Live Analysis)",
        "📧 Email (Darknet Index)",
        "👤 Розыск (ФИО / UA)",
        "🌐 Nickname (Social Trace)",
        "🚗 Авто-Модуль (ГРЗ)",
        "👁 Visual ID (Faces)",
        "📸 EXIF Meta"
    ])
    st.divider()
    st.caption("2026 Operational Terminal | v5.0 Elite")

# --- ЛОГИКА МОДУЛЕЙ ---

# 1. ТЕЛЕФОН (LIVE)
if menu == "📞 Телефон (Live Analysis)":
    st.header("📞 Живой анализ номера")
    phone_input = st.text_input("Введите номер (380...):").strip()
    
    if phone_input:
        num = "".join(filter(str.isdigit, phone_input))
        short_num = num[-10:] if len(num) >= 10 else num
        st.subheader(f"📊 Объект: +{num}")
        
        # Live Parsing
        with st.spinner('Запрос к узлам связи...'):
            geo_info = get_phone_info(num)
            if geo_info and 'name' in geo_info:
                st.markdown(f"""
                <div class="live-box">
                    <b style="color:#2ea043;">[LIVE DATA FOUND]</b><br>
                    📍 <b>Регион:</b> {geo_info.get('country', {}).get('name', 'N/A')}, {geo_info.get('region', {}).get('name', 'N/A')}<br>
                    📡 <b>Оператор:</b> {geo_info.get('0', {}).get('oper', 'N/A')}
                </div>
                """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="data-card"><b>📱 МЕССЕНДЖЕРЫ</b><br>
                <a class="card-link" href="https://t.me/+{num}" target="_blank">TELEGRAM PROFILE</a><br>
                <a class="card-link" href="https://wa.me/{num}" target="_blank">WHATSAPP CHAT</a>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="data-card" style="border-left: 4px solid #d73a49;"><b>🚨 LEAKS & SOCIAL</b><br>
                <a class="card-link" href="https://leakcheck.net/search?type=phone&check={num}" target="_blank">LEAKCHECK (Связки)</a><br>
                <a class="card-link" href="https://www.google.com/search?q=%22{short_num}%22+site:facebook.com+OR+site:vk.com" target="_blank">ПОИСК В СОЦСЕТЯХ</a>
            </div>
            """, unsafe_allow_html=True)

# 2. EMAIL
elif menu == "📧 Email (Darknet Index)":
    st.header("📧 Глубокая разведка по Email")
    email = st.text_input("Введите адрес (example@gmail.com):").strip()
    if email:
        u_nick = email.split('@')[0]
        st.subheader(f"📊 Объект: {email}")
        c_l, c_r = st.columns(2)
        with c_l:
            st.markdown(f"""<div class="data-card"><b>Упоминания ника ({u_nick}):</b><br><a class="card-link" href="https://www.google.com/search?q=%22{u_nick}%22+OR+%22{email}%22" target="_blank">SEARCH GOOGLE</a></div>""", unsafe_allow_html=True)
        with c_r:
            st.markdown(f"""
            <div class="data-card" style="border-left: 4px solid #7928ca;"><b>Darknet Index:</b><br><a class="card-link" href="https://intelx.io/?s={email}" target="_blank">INTELX SEARCH</a></div>
            <div class="data-card" style="border-left: 4px solid #d73a49;"><b>Leaks:</b><br><a class="card-link" href="https://haveibeenpwned.com/account/{email}" target="_blank">HAVE I BEEN PWNED</a></div>
            """, unsafe_allow_html=True)

# 3. ФИО
elif menu == "👤 Розыск (ФИО / UA)":
    st.header("👤 Поиск по реестрам Украины")
    c1, c2, c3 = st.columns(3)
    with c1: ln = st.text_input("Фамилия:")
    with c2: fn = st.text_input("Имя:")
    with c3: mn = st.text_input("Отчество:")
    if ln and fn:
        full_name = f"{ln} {fn} {mn}".strip()
        safe_name = urllib.parse.quote(full_name)
        st.markdown(f"""
        <div class="data-card">🏛 <a class="card-link" href="https://court.gov.ua/fair/" target="_blank">СУДОВА ВЛАДА (Поиск дел)</a></div>
        <div class="data-card">🔍 <a class="card-link" href="https://clarity-project.info/search?q={safe_name}" target="_blank">CLARITY PROJECT (Бизнес и декларации)</a></div>
        """, unsafe_allow_html=True)

# 4. НИКНЕЙМ
elif menu == "🌐 Nickname (Social Trace)":
    st.header("🌐 Поиск по Nickname")
    nick = st.text_input("Введите никнейм (без @):").strip()
    if nick:
        st.markdown(f"""
        <div class="data-card">📸 <a class="card-link" href="https://instagram.com/{nick}" target="_blank">INSTAGRAM</a></div>
        <div class="data-card">🎬 <a class="card-link" href="https://www.tiktok.com/@{nick}" target="_blank">TIKTOK</a></div>
        <div class="data-card">🎮 <a class="card-link" href="https://steamcommunity.com/id/{nick}" target="_blank">STEAM ID</a></div>
        """, unsafe_allow_html=True)

# 5. АВТО
elif menu == "🚗 Авто-Модуль (ГРЗ)":
    st.header("🚗 Проверка транспортного средства")
    plate = st.text_input("Госномер (например BM1976EO):").strip().upper().replace(" ", "")
    if plate:
        st.markdown(f"""
        <div class="data-card">📄 <a class="card-link" href="https://baza-gai.com.ua/nomer/{plate}" target="_blank">ТЕХПАСПОРТ (Baza-GAI)</a></div>
        <div class="data-card">🛑 <a class="card-link" href="https://opendatabot.ua/auto/{plate}" target="_blank">АРЕСТЫ / ЗАЛОГИ (OpenDataBot)</a></div>
        """, unsafe_allow_html=True)

# 6. VISUAL ID
elif menu == "👁 Visual ID (Faces)":
    st.header("👁 Поиск по лицу")
    st.info("Используйте фото из профилей мессенджеров:")
    st.markdown(f"""
    <div class="data-card">🟢 <a class="card-link" href="https://facecheck.id/" target="_blank">FACECHECK.ID (Рекомендую)</a></div>
    <div class="data-card">🔵 <a class="card-link" href="https://pimeyes.com/" target="_blank">PIMEYES</a></div>
    """, unsafe_allow_html=True)

# 7. EXIF
elif menu == "📸 EXIF Meta":
    st.header("📸 Метаданные фото")
    f = st.file_uploader("Загрузите JPG:", type=['jpg', 'jpeg'])
    if f:
        img = Image.open(io.BytesIO(f.read()))
        st.image(img, width=300)
        exif = img._getexif()
        if exif: st.success("Данные успешно извлечены из заголовков файла.")
        else: st.warning("EXIF-данные не найдены.")
