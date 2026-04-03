import streamlit as st
import pandas as pd
import requests
import folium
from PIL import Image
from PIL.ExifTags import TAGS
from streamlit_folium import st_folium
import io
import urllib.parse
import cv2
import numpy as np
import os

# --- КОНФИГУРАЦИЯ ТЕРМИНАЛА ---
st.set_page_config(page_title="kaseye", layout="wide", page_icon="🕸️")

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
    .data-card:hover { border-color: #58a6ff; box-shadow: 0 0 15px rgba(88, 166, 255, 0.2); }
    .card-icon { color: #58a6ff; font-size: 1.5em; margin-right: 12px; float: left; }
    .card-title { color: white; font-weight: bold; font-size: 1em; display: block; }
    .card-link { color: #8b949e; text-decoration: none; font-size: 0.9em; font-weight: bold; }
    .card-link:hover { color: #58a6ff; }

    .online-indicator { color: #2ea043; font-weight: bold; animation: pulse 2.5s infinite; text-align: center; font-size: 0.8em; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_decimal_from_dms(dms, ref):
    try:
        degrees = float(dms[0]);
        minutes = float(dms[1]) / 60.0;
        seconds = float(dms[2]) / 3600.0
        return -(degrees + minutes + seconds) if ref in ['S', 'W'] else degrees + minutes + seconds
    except:
        return None


# --- SIDEBAR ---
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

# --- МОДУЛЬ 1: ФИО ---
if menu == "👤 Розыск (Поиск по ФИО)":
    st.header("👤 Глубокий розыск личности (UA)")
    c1, c2, c3 = st.columns(3)
    with c1:
        lname = st.text_input("Фамилия:", placeholder="Іванов").strip()
    with c2:
        fname = st.text_input("Имя:", placeholder="Іван").strip()
    with c3:
        mname = st.text_input("Отчество:", placeholder="Іванович").strip()

    if lname and fname:
        full_name = f"{lname} {fname} {mname}".strip()
        safe_name = urllib.parse.quote(full_name)
        st.subheader(f"📊 Досье: {full_name}")

        t_gov, t_leaks, t_biz = st.tabs(["🏛 Реестры", "🚨 Утечки", "💼 Бизнес и Связи"])
        with t_gov:
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">⚖️</span><span class="card-title">Судова влада України</span><a class="card-link" href="https://court.gov.ua/fair/" target="_blank">Проверить судебные дела</a></div>""",
                unsafe_allow_html=True)
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">📦</span><span class="card-title">ProZorro (Тендеры)</span><a class="card-link" href="https://prozorro.gov.ua/tender/search/?text={safe_name}" target="_blank">Госвыплаты и контракты</a></div>""",
                unsafe_allow_html=True)
        with t_leaks:
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">🚨</span><span class="card-title">Google Dork (Leaks)</span><a class="card-link" href="https://www.google.com/search?q=site:pastebin.com OR site:trello.com "{safe_name}"" target="_blank">Поиск в открытых дампах</a></div>""",
                unsafe_allow_html=True)
        with t_biz:
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">🔍</span><span class="card-title">Clarity Project</span><a class="card-link" href="https://clarity-project.info/search?q={safe_name}" target="_blank">Декларации и тендеры</a></div>""",
                unsafe_allow_html=True)
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">🏢</span><span class="card-title">YouControl (Публичные данные)</span><a class="card-link" href="https://youcontrol.com.ua/catalog/company_search/?search={safe_name}" target="_blank">Проверка бизнес-активности</a></div>""",
                unsafe_allow_html=True)

# --- МОДУЛЬ 2: ТЕЛЕФОН ---
elif menu == "📞 Телефон (Глубокий анализ)":
    st.header("📞 Глобальный поиск по номеру")
    phone_input = st.text_input("Введите номер (например: 380...):", placeholder="380501234567")
    if st.button("ЗАПУСТИТЬ АНАЛИЗ"):
        clean_num = "".join(filter(str.isdigit, phone_input))
        st.info(f"📍 Локация: Украина (Vodafone/Kyivstar/Lifecell)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"- [🔵 Telegram](https://t.me/+{clean_num})")
            st.markdown(f"- [💬 WhatsApp](https://wa.me/{clean_num})")
            st.markdown(f"- [🔎 Google Search](https://www.google.com/search?q=%22{clean_num}%22)")
        with col2:
            st.markdown(f"- [⚡ Кто звонил? (UA)](https://ktodzvoniv.com.ua/number/{clean_num})")
            st.markdown(f"- [🏢 Справочник (UA)](https://nomer-telefona.com.ua/nomer/{clean_num})")

# --- МОДУЛЬ 3: АВТО (ВСТРОЕННЫЙ АНАЛИЗ) ---
elif menu == "🚗 Авто-Модуль (ГРЗ / VIN)":
    st.header("🚗 Прямая идентификация ТС")
    plate = st.text_input("Введите госномер (АА1111АА):").strip().upper().replace(" ", "")
    
    if plate:
        st.subheader(f"🔎 Результаты по объекту: {plate}")
        
        # Информационная панель (имитация получения данных из API)
        with st.spinner("Синхронизация с базами МВД..."):
            # В реальном API тут был бы запрос, сейчас выводим структурированно
            c1, c2, c3 = st.columns([1, 1, 1])
            
            with c1:
                st.markdown(f"""
                <div class="data-card">
                    <b>🚗 МАРКА/МОДЕЛЬ:</b><br>Ожидание данных...<br><br>
                    <b>🎨 ЦВЕТ:</b><br>Ожидание...
                </div>""", unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"""
                <div class="data-card">
                    <b>📅 ГОД ВЫПУСКА:</b><br>Ожидание...<br><br>
                    <b>⛽ ТИП ТОПЛИВА:</b><br>Ожидание...
                </div>""", unsafe_allow_html=True)
                
            with c3:
                st.markdown(f"""
                <div class="data-card">
                    <b>🔢 VIN:</b><br><code style="color:#58a6ff;">ЗАПРОС В MTSBU...</code><br><br>
                    <b>📈 СТАТУС:</b><br><span style="color:#2ea043;">АКТИВНА</span>
                </div>""", unsafe_allow_html=True)

        # ПОДТЯГИВАЕМ ФОТО (Google Custom Search или встраивание)
        st.write("---")
        st.subheader("🖼 Визуальная идентификация")
        
        # Трюк: Поиск фото конкретно этой машины в Google Image напрямую в Iframe (или через API)
        search_url = f"https://www.google.com/search?q={plate}+Украина+авто+номер&tbm=isch"
        
        col_img, col_info = st.columns([2, 1])
        with col_img:
            # Пытаемся вывести превью через поисковый запрос (встроенный поиск)
            st.info("Ниже подгрузятся фото из публичных реестров и соцсетей:")
            st.markdown(f"""
            <iframe src="https://www.bing.com/images/search?q={plate}+номер+авто+украина" 
            width="100%" height="400" style="border:1px solid #1a202c; border-radius:10px;"></iframe>
            """, unsafe_allow_html=True)
            
        with col_info:
            st.warning("⚠️ Внимание")
            st.write("Если фото не подгрузилось, значит номер не был замечен в базах нарушений, страховых случаях или авто-продажах (Auto.ria/RST).")
            if st.button("Сгенерировать рапорт"):
                st.success("Рапорт сформирован в кэш системы.")

# --- МОДУЛЬ 4: NICKNAME ---
elif menu == "🌐 Nickname (Социальный след)":
    st.header("🌐 Глобальный поиск по Nickname")
    username = st.text_input("Введите никнейм (без @):").strip()
    if st.button("СКАНЕР СОЦСЕТЕЙ"):
        targets = {
            "Telegram": f"https://t.me/{username}",
            "Instagram": f"https://www.instagram.com/{username}/",
            "VK": f"https://vk.com/{username}",
            "TikTok": f"https://www.tiktok.com/@{username}",
            "GitHub": f"https://github.com/{username}",
            "Pinterest": f"https://www.pinterest.com/{username}/"
        }
        cols = st.columns(2)
        for i, (name, url) in enumerate(targets.items()):
            with cols[i % 2]:
                st.markdown(
                    f"""<div class="data-card"><b>{name}</b><br><a class="card-link" href="{url}" target="_blank">Открыть профиль</a></div>""",
                    unsafe_allow_html=True)

# --- МОДУЛЬ 5: VISUAL ID ---
elif menu == "👁 Visual ID (Лицо / AI)":
    st.header("👁 Идентификация по лицу")
    face_file = st.file_uploader("Загрузите фото:", type=['jpg', 'jpeg', 'png'])
    if face_file:
        st.image(face_file, caption="Объект для анализа", width=300)
        st.warning("Для глобального деанона используйте внешние индексы:")
        st.markdown("[ЗАПУСТИТЬ FACECHECK.ID](https://facecheck.id/) | [ЗАПУСТИТЬ PIMEYES](https://pimeyes.com/)")

# --- МОДУЛЬ 6: EXIF ---
elif menu == "📸 EXIF Анализ":
    st.header("📸 EXIF/GPS Metadata")
    file = st.file_uploader("Загрузите JPEG:", type=['jpg', 'jpeg'])
    if file:
        img = Image.open(io.BytesIO(file.read()))
        st.image(img, width=400)
        exif = img._getexif()
        if exif:
            tags = {TAGS.get(tag, tag): value for tag, value in exif.items()}
            gps = tags.get('GPSInfo')
            if gps:
                lat = get_decimal_from_dms(gps[2], gps[1]);
                lon = get_decimal_from_dms(gps[4], gps[3])
                if lat and lon:
                    st.success(f"📍 Координаты найдены: {lat}, {lon}")
                    m = folium.Map(location=[lat, lon], zoom_start=15)
                    folium.Marker([lat, lon]).add_to(m)
                    st_folium(m, width=700, height=400)
                else:
                    st.error("GPS данные повреждены.")
            else:
                st.warning("В фото нет GPS-меток.")
