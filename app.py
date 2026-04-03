import streamlit as st
import pandas as pd
import requests
import folium
from PIL import Image
from PIL.ExifTags import TAGS
from streamlit_folium import st_folium
import io
import urllib.parse
import re
import cv2
import numpy as np
import os

# --- КОНФИГУРАЦИЯ ПОДКЛЮЧЕНИЯ ---
# Вставь сюда актуальную ссылку из ngrok
SF_URL = "https://paola-brickish-reprovingly.ngrok-free.dev"

# --- КОНФИГУРАЦИЯ kaseye v4.4 ---
st.set_page_config(page_title="kaseye", layout="wide", page_icon="🕸️")

# --- ГЛОБАЛЬНЫЙ КИБЕР-ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e0e6ed; font-family: 'Consolas', monospace; }
    [data-testid="stSidebar"] { background-color: rgba(10, 13, 18, 0.95) !important; border-right: 2px solid #1a202c; }

    .sidebar-title {
        color: #58a6ff; font-size: 24px; font-weight: 800; text-shadow: 0 0 15px rgba(88, 166, 255, 0.5);
        text-align: center; margin-bottom: 20px; letter-spacing: 2px;
    }

    .stButton>button { 
        width: 100%; background-image: linear-gradient(135deg, #d73a49 0%, #a71a26 100%);
        color: white; border-radius: 4px; font-weight: bold; border: 1px solid #ff7b72; 
        height: 3.5em; text-transform: uppercase; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(215, 58, 73, 0.8); transform: translateY(-2px); }

    h1, h2, h3 { color: #58a6ff; text-shadow: 0 0 10px rgba(88, 166, 255, 0.4); }
    .stTextInput>div>div>input { background-color: #0d1117; color: #ffffff; border: 1px solid #30363d; }

    .data-card {
        background-color: rgba(16, 20, 27, 0.9); border: 1px solid #1a202c;
        border-radius: 8px; padding: 20px; margin-bottom: 15px; transition: 0.3s;
    }
    .data-card:hover { border-color: #58a6ff; box-shadow: 0 0 15px rgba(88, 166, 255, 0.2); }
    .card-icon { color: #58a6ff; font-size: 1.8em; margin-right: 15px; float: left; }
    .card-title { color: white; font-weight: bold; font-size: 1.1em; display: block; }
    .card-link { color: #8b949e; text-decoration: none; margin-top: 5px; display: inline-block; font-weight: bold; }
    .card-link:hover { color: #58a6ff; }

    .online-indicator { color: #2ea043; font-weight: bold; animation: pulse 2.5s infinite; text-align: center; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_decimal_from_dms(dms, ref):
    try:
        degrees = float(dms[0])
        minutes = float(dms[1]) / 60.0
        seconds = float(dms[2]) / 3600.0
        return -(degrees + minutes + seconds) if ref in ['S', 'W'] else degrees + minutes + seconds
    except:
        return None

# --- SIDEBAR (БОКОВАЯ ПАНЕЛЬ) ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>KASEYE </div>", unsafe_allow_html=True)
    st.markdown("<p class='online-indicator'>● СТАТУС: ONLINE</p>", unsafe_allow_html=True)
    st.divider()
    
    # Объединенное меню
    menu = st.radio("ВЕКТОРЫ РАЗВЕДКИ:", [
        "🏠 Главная (Инфо)",
        "🕵️ SpiderFoot (Глобальный движок)",
        "👤 Розыск (Поиск по ФИО)",
        "📧 Email (Проверка почты)",
        "📞 Телефон (Поиск по номеру)",
        "🌐 Nickname (Поиск по нику)",
        "👁 Visual ID (Лицо)",
        "📸 EXIF Анализ"
    ])
    
    st.divider()
    st.caption("2026 Operational Terminal | v4.4 Apex")

# --- ЛОГИКА ОТОБРАЖЕНИЯ МОДУЛЕЙ ---

if menu == "🏠 Главная (Инфо)":
    st.title("Добро пожаловать в KASEYE v4.4")
    st.write("Выберите модуль в боковой панели для начала работы.")
    st.info("Для работы SpiderFoot убедитесь, что локальный сервер и ngrok запущены.")

elif menu == "🕵️ SpiderFoot (Глобальный движок)":
    st.header("🕵️ SpiderFoot: Deep Recon Engine")
    if SF_URL:
        st.components.v1.iframe(SF_URL, height=900, scrolling=True)
    else:
        st.error("Ссылка SF_URL не найдена. Проверьте конфигурацию в коде.")

elif menu == "👤 Розыск (Поиск по ФИО)":
    st.header("👤 Глубокий розыск личности")
    c1, c2, c3 = st.columns(3)
    with c1: lname = st.text_input("Фамилия (Укр):", placeholder="Іванов").strip()
    with c2: fname = st.text_input("Имя (Укр):", placeholder="Іван").strip()
    with c3: mname = st.text_input("Отчество (Укр):", placeholder="Іванович").strip()

    if lname and fname:
        full_name = f"{lname} {fname} {mname}".strip()
        safe_name = urllib.parse.quote(full_name)
        st.subheader(f"📊 Досье: {full_name}")
        t_gov, t_leaks, t_biz = st.tabs(["🏛 Реестры", "🚨 Утечки", "💼 Бизнес"])
        with t_gov:
            st.markdown(f"""<div class="data-card"><span class="card-icon">📦</span><span class="card-title">ProZorro</span><a class="card-link" href="https://prozorro.gov.ua/tender/search/?text={safe_name}" target="_blank">Проверить выплаты</a></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="data-card"><span class="card-icon">⚖️</span><span class="card-title">Судова влада</span><a class="card-link" href="https://court.gov.ua/fair/" target="_blank">Судебные дела</a></div>""", unsafe_allow_html=True)
        with t_leaks:
            leak_dork = f'site:pastebin.com OR site:trello.com "{full_name}"'
            st.markdown(f"""<div class="data-card"><span class="card-icon">🚨</span><span class="card-title">Leaks Hunter</span><a class="card-link" href="https://www.google.com/search?q={urllib.parse.quote(leak_dork)}" target="_blank">Искать в дампах</a></div>""", unsafe_allow_html=True)
        with t_biz:
            st.markdown(f"""<div class="data-card"><span class="card-icon">🔍</span><span class="card-title">Clarity Project</span><a class="card-link" href="https://clarity-project.info/search?q={safe_name}" target="_blank">Связи и декларации</a></div>""", unsafe_allow_html=True)

elif menu == "📧 Email (Проверка почты)":
    st.header("📧 Email Analysis")
    email_input = st.text_input("Введите Email адрес:").strip()
    if email_input:
        c1, c2 = st.columns(2)
        with c1: st.markdown(f"""<div class="data-card"><span class="card-icon">🔓</span><span class="card-title">HIBP</span><a class="card-link" href="https://haveibeenpwned.com/account/{email_input}" target="_blank">Проверить взломы</a></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="data-card"><span class="card-icon">👁</span><span class="card-title">IntelX</span><a class="card-link" href="https://intelx.io/?s={email_input}" target="_blank">Поиск в архивах</a></div>""", unsafe_allow_html=True)

elif menu == "📞 Телефон (Поиск по номеру)":
    st.header("📞 Поиск по номеру телефона")
    phone_input = st.text_input("Введите номер (380...):")
    if st.button("АНАЛИЗ НОМЕРА"):
        clean_num = "".join(filter(str.isdigit, phone_input))
        st.info(f"Анализ номера: +{clean_num}")
        st.markdown(f"- [🔵 Telegram](https://t.me/+{clean_num})")
        st.markdown(f"- [🔍 Google Search](https://www.google.com/search?q=%22{clean_num}%22)")

elif menu == "🌐 Nickname (Поиск по нику)":
    st.header("🌐 Поиск по Nickname")
    username = st.text_input("Введите никнейм (без @):").strip()
    if st.button("СКАНЕР"):
        st.success(f"Запущен поиск для: {username}")
        st.markdown(f"- [GitHub](https://github.com/{username})")
        st.markdown(f"- [Instagram](https://www.instagram.com/{username}/)")

elif menu == "👁 Visual ID (Лицо)":
    st.header("👁 Neural Vision Engine")
    face_file = st.file_uploader("Загрузите фото:", type=['jpg', 'jpeg', 'png'])
    if face_file:
        st.image(face_file, caption="Загруженное изображение", use_container_width=True)
        st.warning("Локальный нейросетевой анализ требует наличия моделей .prototxt на сервере.")

elif menu == "📸 EXIF Анализ":
    st.header("📸 EXIF/GPS Metadata")
    file = st.file_uploader("Загрузите фото для анализа метаданных:", type=['jpg', 'jpeg'])
    if file:
        img = Image.open(io.BytesIO(file.read()))
        st.image(img, width=400)
        exif = img._getexif()
        if exif:
            tags = {TAGS.get(tag, tag): value for tag, value in exif.items()}
            st.write(f"Устройство: {tags.get('Model', 'N/A')}")
            gps = tags.get('GPSInfo')
            if gps:
                lat = get_decimal_from_dms(gps[2], gps[1])
                lon = get_decimal_from_dms(gps[4], gps[3])
                if lat and lon:
                    st.success(f"📍 Координаты: {lat}, {lon}")
                    m = folium.Map(location=[lat, lon], zoom_start=15)
                    folium.Marker([lat, lon]).add_to(m)
                    st_folium(m, width=800, height=450)
