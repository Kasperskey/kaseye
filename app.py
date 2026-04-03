import streamlit as st
import pandas as pd
from PIL import Image
import io
import urllib.parse

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="kaseye", layout="wide", page_icon="🕸️")

# --- СТИЛИ (КИБЕР-ДИЗАЙН) ---
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e0e6ed; font-family: 'Consolas', monospace; }
    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .data-card {
        background-color: #161b22; border: 1px solid #30363d;
        border-radius: 8px; padding: 15px; margin-bottom: 10px;
    }
    .card-link { color: #58a6ff !important; text-decoration: none; font-weight: bold; font-size: 1.1em; }
    .card-link:hover { text-decoration: underline; color: #1f6feb !important; }
    .online-indicator { color: #2ea043; font-weight: bold; animation: pulse 2.5s infinite; text-align: center; font-size: 0.8em; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#58a6ff;'>🕸️ KASEYE</h2>", unsafe_allow_html=True)
    st.markdown("<p class='online-indicator'>● SYSTEM | ONLINE </p>", unsafe_allow_html=True)
    st.divider()

    menu = st.radio("Возможности:", [
        "📞 ТЕЛЕФОН", 
        "📧 EMAIL", 
        "👤 ФИО (UA)", 
        "🌐 NICKNAME", 
        "🚗 АВТО", 
        "👁 ЛИЦО", 
        "📸 EXIF"
    ])
    st.divider()
    st.caption("Deep Search | 2026")

# --- ЛОГИКА МОДУЛЕЙ ---

# 1. ТЕЛЕФОН (ОБНОВЛЕННЫЙ ГЛУБОКИЙ ПОИСК)
if menu == "📞 ТЕЛЕФОН":
    st.header("📞 Анализ номера")
    phone = st.text_input("Введите номер (380...):").strip()
    
    if phone:
        num = "".join(filter(str.isdigit, phone))
        short = num[-10:] if len(num) >= 10 else num
        # Формат для поиска: 050 132 77 13
        formatted = f"{short[:3]} {short[3:6]} {short[6:8]} {short[8:]}"
        
        st.subheader(f"📊 Объект: +{num}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="data-card">
                <b>🌍 СОЦСЕТИ (Глобал)</b><br>
                <a class="card-link" href="https://www.google.com/search?q=%22{short}%22+site:facebook.com+OR+site:instagram.com" target="_blank">🔎 Найти в FB / IG</a><br>
                <a class="card-link" href="https://www.google.com/search?q=%22{short}%22+OR+%22{formatted}%22+site:vk.com+OR+site:ok.ru" target="_blank">🔎 Найти в VK / OK</a>
            </div>
            <div class="data-card">
                <b>📦 ДОСКИ ОБЪЯВЛЕНИЙ (UA)</b><br>
                <a class="card-link" href="https://www.google.com/search?q=%22{short}%22+OR+%22{formatted}%22+site:olx.ua+OR+site:izi.ua" target="_blank">🔎 OLX / IZI / Kabanchik</a>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
            <div class="data-card">
                <b>📱 МЕССЕНДЖЕРЫ</b><br>
                <a class="card-link" href="https://t.me/+{num}" target="_blank">TELEGRAM</a> | 
                <a class="card-link" href="https://wa.me/{num}" target="_blank">WHATSAPP</a>
            </div>
            <div class="data-card" style="border-left: 4px solid #d73a49;">
                <b>🚨 УТЕЧКИ ДАННЫХ</b><br>
                <a class="card-link" href="https://leakcheck.net/search?type=phone&check={num}" target="_blank">LEAKCHECK (Связки)</a>
            </div>
            """, unsafe_allow_html=True)

# 2. EMAIL
elif menu == "📧 EMAIL":
    st.header("📧 Поиск по Email")
    email = st.text_input("Введите адрес:").strip()
    if email:
        st.markdown(f'<div class="data-card">🌑 <a class="card-link" href="https://intelx.io/?s={email}" target="_blank">IntelX (Darknet Search)</a></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-card">🚨 <a class="card-link" href="https://haveibeenpwned.com/account/{email}" target="_blank">HaveIBeenPwned</a></div>', unsafe_allow_html=True)

# 3. ФИО (UA)
elif menu == "👤 ФИО (UA)":
    st.header("👤 Реестры Украины")
    f = st.text_input("Фамилия:")
    i = st.text_input("Имя:")
    if f and i:
        safe_name = urllib.parse.quote(f"{f} {i}")
        st.markdown(f'<div class="data-card">⚖️ <a class="card-link" href="https://court.gov.ua/fair/" target="_blank">Судовая влада</a></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-card">🔍 <a class="card-link" href="https://clarity-project.info/search?q={safe_name}" target="_blank">Clarity Project</a></div>', unsafe_allow_html=True)

# 4. NICKNAME
elif menu == "🌐 NICKNAME":
    st.header("🌐 Поиск ника")
    nick = st.text_input("Никнейм (без @):").strip()
    if nick:
        st.markdown(f'<div class="data-card">📸 <a class="card-link" href="https://instagram.com/{nick}" target="_blank">Instagram</a></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-card">💬 <a class="card-link" href="https://www.google.com/search?q=%22{nick}%22" target="_blank">Google Search</a></div>', unsafe_allow_html=True)

# 5. АВТО
elif menu == "🚗 АВТО":
    st.header("🚗 Госномер")
    plate = st.text_input("Номер (BM1976EO):").upper().replace(" ","")
    if plate:
        st.markdown(f'<div class="data-card">📄 <a class="card-link" href="https://baza-gai.com.ua/nomer/{plate}" target="_blank">Техпаспорт</a></div>', unsafe_allow_html=True)

# 6. VISUAL ID
elif menu == "👁 VISUAL ID":
    st.header("👁 Поиск по лицу")
    st.markdown('<div class="data-card">🟢 <a class="card-link" href="https://facecheck.id/" target="_blank">FaceCheck.ID</a></div>', unsafe_allow_html=True)
    st.markdown('<div class="data-card">🔵 <a class="card-link" href="https://pimeyes.com/" target="_blank">PimEyes</a></div>', unsafe_allow_html=True)

# 7. EXIF
elif menu == "📸 EXIF":
    st.header("📸 Анализ метаданных")
    file = st.file_uploader("Загрузите фото:", type=['jpg', 'jpeg'])
    if file:
        img = Image.open(io.BytesIO(file.read()))
        st.image(img, width=300)
        st.success("Метаданные готовы к анализу (если они не удалены).")
