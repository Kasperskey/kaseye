import streamlit as st
import pandas as pd
import requests
import folium
from PIL import Image
from PIL.ExifTags import TAGS
from streamlit_folium import st_folium
import io
import urllib.parse

# --- КОНФИГУРАЦИЯ ТЕРМИНАЛА ---
st.set_page_config(page_title="KASEYE Elite", layout="wide", page_icon="🕸️")

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
        background-color: rgba(16, 20, 27, 0.9); border: 1px solid #1a202c;
        border-radius: 8px; padding: 15px; margin-bottom: 10px; transition: 0.3s;
        border-left: 4px solid #58a6ff;
    }
    .card-icon { color: #58a6ff; font-size: 1.5em; margin-right: 12px; float: left; }
    .card-title { color: white; font-weight: bold; font-size: 1em; display: block; }
    .card-link { color: #58a6ff !important; text-decoration: none; font-size: 0.9em; font-weight: bold; }
    .card-link:hover { text-shadow: 0 0 10px #58a6ff; }
    .online-indicator { color: #2ea043; font-weight: bold; animation: pulse 2.5s infinite; text-align: center; font-size: 0.8em; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_decimal_from_dms(dms, ref):
    try:
        degrees = float(dms[0]); minutes = float(dms[1]) / 60.0; seconds = float(dms[2]) / 3600.0
        return -(degrees + minutes + seconds) if ref in ['S', 'W'] else degrees + minutes + seconds
    except: return None

# --- SIDEBAR (БЕЗ СТИКЕРА) ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>KASEYE</div>", unsafe_allow_html=True)
    st.markdown("<p class='online-indicator'>● СИСТЕМА: OPERATIONAL</p>", unsafe_allow_html=True)
    st.divider()

    menu = st.radio("ВЕКТОРЫ РАЗВЕДКИ:", [
        "👤 Розыск (Поиск по ФИО)",
        "📞 Телефон (Глубокий анализ)",
        "🚗 Авто-Модуль (ГРЗ / VIN)",
        "🌐 Nickname (Социальный след)",
        "📧 Email (Утечки и профили)",
        "👁 Visual ID (Лицо / AI)",
        "📸 EXIF Анализ"
    ])
    st.divider()
    st.caption("2026 Operational Terminal | v4.5 Elite")

# --- ЛОГИКА ОТОБРАЖЕНИЯ ---

if menu == "👤 Розыск (Поиск по ФИО)":
    st.header("👤 Глубокий розыск личности (UA)")
    c1, c2, c3 = st.columns(3)
    with c1: lname = st.text_input("Фамилия:").strip()
    with c2: fname = st.text_input("Имя:").strip()
    with c3: mname = st.text_input("Отчество:").strip()
    if lname and fname:
        fn = f"{lname} {fname} {mname}".strip()
        safe_fn = urllib.parse.quote(fn)
        st.subheader(f"📊 Досье: {fn}")
        t1, t2 = st.tabs(["🏛 Реестры", "💼 Бизнес"])
        with t1:
            st.markdown(f"""<div class="data-card"><span class="card-icon">⚖️</span><a class="card-link" href="https://court.gov.ua/fair/" target="_blank">СУДОВА ВЛАДА (Поиск дел)</a></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="data-card"><span class="card-icon">📦</span><a class="card-link" href="https://prozorro.gov.ua/tender/search/?text={safe_fn}" target="_blank">PROZORRO (Тендеры)</a></div>""", unsafe_allow_html=True)
        with t2:
            st.markdown(f"""<div class="data-card"><span class="card-icon">🔍</span><a class="card-link" href="https://clarity-project.info/search?q={safe_fn}" target="_blank">CLARITY PROJECT (Декларации)</a></div>""", unsafe_allow_html=True)

elif menu == "📞 Телефон (Глубокий анализ)":
    st.header("📞 Поиск по номеру телефона")
    phone = st.text_input("Введите номер (380...):")
    if phone:
        num = "".join(filter(str.isdigit, phone))
        st.markdown(f"""<div class="data-card"><b>Telegram:</b> <a class="card-link" href="https://t.me/+{num}" target="_blank">ОТКРЫТЬ ПРОФИЛЬ</a></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="data-card"><b>База отзывов:</b> <a class="card-link" href="https://ktodzvoniv.com.ua/number/{num}" target="_blank">КТО ЗВОНИЛ (UA)</a></div>""", unsafe_allow_html=True)

elif menu == "🚗 Авто-Модуль (ГРЗ / VIN)":
    st.header("🚗 Идентификация транспортного средства")
    plate = st.text_input("Введите госномер (BM9971AX):").strip().upper().replace(" ", "")
    if plate:
        st.subheader(f"🔎 Объект: {plate}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="data-card">📑 <b>ТЕХПАСПОРТ</b><br><a class="card-link" href="https://baza-gai.com.ua/nomer/{plate}" target="_blank">ХАРАКТЕРИСТИКИ (Baza-GAI)</a></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="data-card">👤 <b>ВЛАДЕЛЬЦЫ</b><br><a class="card-link" href="https://opendatabot.ua/auto/{plate}" target="_blank">ИСТОРИЯ (OpenDataBot)</a></div>""", unsafe_allow_html=True)

elif menu == "🌐 Nickname (Социальный след)":
    st.header("🌐 Поиск по Nickname")
    nick = st.text_input("Введите никнейм (без @):").strip()
    if nick:
        st.subheader(f"🔍 След ника: {nick}")
        st.markdown(f"""
        <div class="data-card"><b>Instagram:</b> <a class="card-link" href="https://instagram.com/{nick}" target="_blank">ОТКРЫТЬ</a></div>
        <div class="data-card"><b>TikTok:</b> <a class="card-link" href="https://www.tiktok.com/@{nick}" target="_blank">ОТКРЫТЬ</a></div>
        <div class="data-card"><b>GitHub:</b> <a class="card-link" href="https://github.com/{nick}" target="_blank">ОТКРЫТЬ</a></div>
        <div class="data-card"><b>Steam:</b> <a class="card-link" href="https://steamcommunity.com/id/{nick}" target="_blank">ОТКРЫТЬ</a></div>
        """, unsafe_allow_html=True)

elif menu == "📧 Email (Утечки и профили)":
    st.header("📧 Разведка по Email")
    email = st.text_input("Введите адрес (example@gmail.com):").strip()
    if email:
        st.subheader(f"📊 Анализ объекта: {email}")
        col_leaks, col_social = st.columns(2)
        with col_leaks:
            st.markdown("### 🚨 Утечки данных")
            st.markdown(f"""
            <div class="data-card" style="border-left: 4px solid #d73a49;">
                <b>IntelX Даркнет</b><br>
                <a class="card-link" href="https://intelx.io/?s={email}" target="_blank">ПОИСК ПАРОЛЕЙ</a>
            </div>
            <div class="data-card">
                <b>Have I Been Pwned</b><br>
                <a class="card-link" href="https://haveibeenpwned.com/account/{email}" target="_blank">ГДЕ УТЕКЛА ПОЧТА</a>
            </div>
            """, unsafe_allow_html=True)
        with col_social:
            st.markdown("### 🌐 Социальные связи")
            u_nick = email.split('@')[0]
            st.markdown(f"""
            <div class="data-card" style="border-left: 4px solid #58a6ff;">
                <b>OSINT Industries</b><br>
                <a class="card-link" href="https://osint.industries/search?type=email&query={email}" target="_blank">ПРОВЕРИТЬ 100+ АККАУНТОВ</a>
            </div>
            <div class="data-card">
                <b>Поиск по никнейму ({u_nick})</b><br>
                <a class="card-link" href="https://www.google.com/search?q=site:facebook.com+OR+site:instagram.com+{u_nick}" target="_blank">СВЯЗИ В СОЦСЕТЯХ</a>
            </div>
            """, unsafe_allow_html=True)

elif menu == "👁 Visual ID (Лицо / AI)":
    st.header("👁 Идентификация личности по фото")
    st.info("Внешние индексы для поиска совпадений:")
    st.markdown(f"""
    <div class="data-card"><a class="card-link" href="https://facecheck.id/" target="_blank">FACECHECK.ID (Глобальный поиск)</a></div>
    <div class="data-card"><a class="card-link" href="https://pimeyes.com/" target="_blank">PIMEYES (Поиск по лицам)</a></div>
    """, unsafe_allow_html=True)

elif menu == "📸 EXIF Анализ":
    st.header("📸 Извлечение метаданных")
    f = st.file_uploader("Загрузите файл (JPG):", type=['jpg', 'jpeg'])
    if f:
        img = Image.open(io.BytesIO(f.read()))
        st.image(img, width=400)
        exif_data = img._getexif()
        if exif_data:
            st.success("Метаданные найдены.")
        else:
            st.warning("Метаданные отсутствуют.")
