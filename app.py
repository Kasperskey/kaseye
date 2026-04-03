import streamlit as st
import pandas as pd
import requests
from PIL import Image
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
    .card-title { color: white; font-weight: bold; font-size: 1.1em; display: block; }
    .card-link { color: #58a6ff !important; text-decoration: none; font-size: 1em; font-weight: bold; }
    .card-link:hover { text-shadow: 0 0 10px #58a6ff; }
    .online-indicator { color: #2ea043; font-weight: bold; animation: pulse 2.5s infinite; text-align: center; font-size: 0.8em; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

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

# --- ЛОГИКА ОТОБРАЖЕНИЯ ---

# 1. ФИО
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
        st.markdown(f"""
        <div class="data-card"><a class="card-link" href="https://court.gov.ua/fair/" target="_blank">🏛 СУДОВА ВЛАДА (Поиск дел)</a></div>
        <div class="data-card"><a class="card-link" href="https://clarity-project.info/search?q={safe_fn}" target="_blank">🔍 CLARITY PROJECT (Бизнес и связи)</a></div>
        """, unsafe_allow_html=True)

# 2. ТЕЛЕФОН (ПРЯМОЙ ПРОБИВ СОЦСЕТЕЙ)
elif menu == "📞 Телефон (Глубокий анализ)":
    st.header("📞 Глобальный анализ номера")
    phone = st.text_input("Введите номер (380...):").strip()
    if phone:
        num = "".join(filter(str.isdigit, phone))
        # Чистый номер без кода страны (0505653901)
        short_num = num[-10:] if len(num) >= 10 else num
        
        st.subheader(f"📊 Объект: +{num}")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(f"""
            <div class="data-card"><b>📱 МЕССЕНДЖЕРЫ</b><br>
                <a class="card-link" href="https://t.me/+{num}" target="_blank">✅ TELEGRAM (Профиль)</a><br>
                <a class="card-link" href="https://wa.me/{num}" target="_blank">✅ WHATSAPP (Фото/Статус)</a>
            </div>
            <div class="data-card" style="border-left: 4px solid #4267B2;"><b>👥 FACEBOOK (Внутренний поиск)</b><br>
                <a class="card-link" href="https://www.facebook.com/search/top/?q={num}" target="_blank">ИСКАТЬ ПО ПОЛНОМУ НОМЕРУ</a><br>
                <a class="card-link" href="https://www.facebook.com/search/top/?q={short_num}" target="_blank">ИСКАТЬ ПО КОРОТКОМУ НОМЕРУ</a><br>
                <small>Если не нашло, попробуй восстановить пароль по этому номеру — FB покажет имя и фото.</small>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
            <div class="data-card" style="border-left: 4px solid #4c75a3;"><b>🇷🇺 ВК / ОК (Прямые шлюзы)</b><br>
                <a class="card-link" href="https://vk.com/search?c%5Bq%5D={num}&c%5Bsection%5D=people" target="_blank">ВКОНТАКТЕ (Поиск людей)</a><br>
                <a class="card-link" href="https://ok.ru/search?st.query={num}" target="_blank">ОДНОКЛАССНИКИ (Поиск людей)</a><br>
                <small>Важно: В ВК/ОК нужно быть залогиненным, иначе поиск ничего не выдаст.</small>
            </div>
            <div class="data-card" style="border-left: 4px solid #d73a49;"><b>🚨 DARKNET / LEAKS (База связей)</b><br>
                <a class="card-link" href="https://leakcheck.net/search?type=phone&check={num}" target="_blank">LEAKCHECK (Найти Email владельца)</a><br>
                <small>Если найдешь Email, то через него найдем соцсети на 100%.</small>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.info("💡 OSINT-ХАК: Зайди в Facebook/VK 'Забыл пароль', введи номер. Соцсеть сама выведет: 'Это вы? [ИМЯ/ФОТО]'. Это самый точный способ.")
# 3. АВТО
elif menu == "🚗 Авто-Модуль (ГРЗ / VIN)":
    st.header("🚗 Идентификация транспортного средства")
    plate = st.text_input("Введите госномер (например BM1976EO):").strip().upper().replace(" ", "")
    if plate:
        st.subheader(f"🔎 Объект: {plate}")
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown(f"""<div class="data-card"><b>Характеристики (МВД):</b><br><a class="card-link" href="https://baza-gai.com.ua/nomer/{plate}" target="_blank">ТЕХПАСПОРТ (Baza-GAI)</a></div>""", unsafe_allow_html=True)
        with c_right:
            st.markdown(f"""<div class="data-card" style="border-left: 4px solid #ffcc00;"><b>История и Аресты:</b><br><a class="card-link" href="https://opendatabot.ua/auto/{plate}" target="_blank">ПРОВЕРИТЬ (OpenDataBot)</a></div>""", unsafe_allow_html=True)

# 4. НИКНЕЙМ
elif menu == "🌐 Nickname (Социальный след)":
    st.header("🌐 Поиск по Nickname")
    nick = st.text_input("Введите никнейм (без @):").strip()
    if nick:
        st.subheader(f"🔍 Анализ ника: {nick}")
        st.markdown(f"""<div class="data-card"><b>Google Global Search:</b><br><a class="card-link" href="https://www.google.com/search?q=%22{nick}%22" target="_blank">НАЙТИ УПОМИНАНИЯ В СЕТИ</a></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="data-card"><b>Social Networks:</b><br><a class="card-link" href="https://www.google.com/search?q=site:instagram.com+OR+site:facebook.com+OR+site:tiktok.com+%22{nick}%22" target="_blank">ПРОВЕРИТЬ ПРОФИЛИ</a></div>""", unsafe_allow_html=True)

# 5. EMAIL + DARKNET
elif menu == "📧 Email (Утечки и профили)":
    st.header("📧 Глубокая разведка по Email")
    email_input = st.text_input("Введите адрес (example@gmail.com):").strip()
    if email_input:
        st.subheader(f"📊 Объект: {email_input}")
        u_nick = email_input.split('@')[0]
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown(f"""<div class="data-card"><b>Поиск ника ({u_nick}):</b><br><a class="card-link" href="https://www.google.com/search?q=%22{u_nick}%22+OR+%22{email_input}%22" target="_blank">ИСКАТЬ УПОМИНАНИЯ</a></div>""", unsafe_allow_html=True)
        with c_right:
            st.markdown(f"""<div class="data-card" style="border-left: 4px solid #7928ca;"><b>Darknet Index:</b><br><a class="card-link" href="https://intelx.io/?s={email_input}" target="_blank">ПОИСК (IntelX)</a></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="data-card" style="border-left: 4px solid #d73a49;"><b>Leaks Check:</b><br><a class="card-link" href="https://haveibeenpwned.com/account/{email_input}" target="_blank">УТЕЧКИ (HIBP)</a></div>""", unsafe_allow_html=True)

# 6. VISUAL ID
# 6. VISUAL ID (ULTIMATE FACE SEARCH)
elif menu == "👁 Visual ID (Лицо / AI)":
    st.header("👁 Идентификация по лицу")
    st.write("Если номер и почта молчат, лицо — единственный шанс.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="data-card" style="border-left: 4px solid #00ff00;">
            <b>FaceCheck.ID (Рекомендую)</b><br>
            <a class="card-link" href="https://facecheck.id/" target="_blank">ИСКАТЬ ПО ВСЕМ СОЦСЕТЯМ</a><br>
            <small>Находит профили в ВК, FB, Инсте и даже статьи в новостях по фото.</small>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="data-card">
            <b>PimEyes (Deep Search)</b><br>
            <a class="card-link" href="https://pimeyes.com/" target="_blank">ПОИСК ПО ВСЕМУ ИНТЕРНЕТУ</a><br>
            <small>Очень мощный, но часто требует подписку для просмотра ссылок.</small>
        </div>
        """, unsafe_allow_html=True)
        
    st.info("💡 OSINT-СОВЕТ: Сделай скриншот аватарки из WhatsApp или Telegram и загрузи его в FaceCheck. В 90% случаев он найдет его старый ВК или Фейсбук.")

# 7. EXIF
elif menu == "📸 EXIF Анализ":
    st.header("📸 Извлечение метаданных")
    f = st.file_uploader("Загрузите файл (JPG):", type=['jpg', 'jpeg'])
    if f:
        img = Image.open(io.BytesIO(f.read()))
        st.image(img, width=400)
        exif = img._getexif()
        if exif: st.success("Метаданные найдены.")
        else: st.warning("Метаданные отсутствуют.")
