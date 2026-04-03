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
import streamlit as st
#import mediapipe as mp
# --- КОНФИГУРАЦИЯ ПОДКЛЮЧЕНИЯ ---
# Вставь сюда ссылку, которую выдаст ngrok
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

# В боковой панели создаем выбор
menu = st.sidebar.radio("Навигация", ["Главная", "SpiderFoot Разведка"])

if menu == "SpiderFoot Разведка":
    st.subheader("Интерфейс SpiderFoot")
    st.components.v1.iframe(SF_URL, height=900, scrolling=True)
else:
    st.write("Добро пожаловать в KASEYE. Выберите модуль в меню.")

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
        degrees = float(dms[0]);
        minutes = float(dms[1]) / 60.0;
        seconds = float(dms[2]) / 3600.0
        return -(degrees + minutes + seconds) if ref in ['S', 'W'] else degrees + minutes + seconds
    except:
        return None


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>KASEYE </div>", unsafe_allow_html=True)
    st.markdown("<p class='online-indicator'>● СТАТУС: ONLINE</p>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("ВЕКТОРЫ РАЗВЕДКИ:", [
        "👤 Розыск (Поиск по ФИО)",
        "📧 Email (Проверка почты)",
        "📞 Телефонный модуль (Поиск по телефону)",
        "🌐 Nickname (Поиск по никнейму)",
        "👁 Visual ID (Лицо)",
        "📸 EXIF Анализ"
    ])
    st.divider()
    st.caption("2026 Operational Terminal | v4.4 Apex")

# --- МОДУЛЬ 1: ФИО ---
if menu == "👤 Розыск (Поиск по ФИО)":
    st.header("👤 Глубокий розыск личности")
    c1, c2, c3 = st.columns(3)
    with c1:
        lname = st.text_input("Фамилия (Укр):", placeholder="Іванов").strip()
    with c2:
        fname = st.text_input("Имя (Укр):", placeholder="Іван").strip()
    with c3:
        mname = st.text_input("Отчество (Укр):", placeholder="Іванович").strip()

    if lname and fname:
        full_name = f"{lname} {fname} {mname}".strip()
        safe_name = urllib.parse.quote(full_name)
        st.subheader(f"📊 Досье: {full_name}");
        st.code(full_name)

        t_gov, t_leaks, t_biz = st.tabs(["🏛 Реестры", "🚨 Утечки", "💼 Бизнес"])
        with t_gov:
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">📦</span><span class="card-title">ProZorro (Тендеры)</span><a class="card-link" href="https://prozorro.gov.ua/tender/search/?text={safe_name}" target="_blank">Проверить выплаты</a></div>""",
                unsafe_allow_html=True)
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">⚖️</span><span class="card-title">Судова влада</span><a class="card-link" href="https://court.gov.ua/fair/" target="_blank">Судебные дела (Manual)</a></div>""",
                unsafe_allow_html=True)
        with t_leaks:
            leak_dork = f'site:pastebin.com OR site:trello.com "{full_name}"'
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">🚨</span><span class="card-title">Leaks Hunter</span><a class="card-link" href="https://www.google.com/search?q={urllib.parse.quote(leak_dork)}" target="_blank">Искать в дампах</a></div>""",
                unsafe_allow_html=True)
        with t_biz:
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">🔍</span><span class="card-title">Clarity Project</span><a class="card-link" href="https://clarity-project.info/search?q={safe_name}" target="_blank">Связи и декларации</a></div>""",
                unsafe_allow_html=True)

# --- МОДУЛЬ 2: EMAIL (BREACH ANALYSIS) ---
elif menu == "📧 Email (Проверка почты)":
    st.header("📧 Проверка Email на утечки и взломы")
    email_input = st.text_input("Введите Email адрес:", placeholder="").strip()
    if email_input:
        st.subheader(f"🔐 Анализ: {email_input}");
        st.code(email_input)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">🔓</span><span class="card-title">Have I Been Pwned</span><a class="card-link" href="https://haveibeenpwned.com/account/{email_input}" target="_blank">Проверить на взломы</a></div>""",
                unsafe_allow_html=True)
        with c2:
            st.markdown(
                f"""<div class="data-card"><span class="card-icon">👁</span><span class="card-title">IntelX Search</span><a class="card-link" href="https://intelx.io/?s={email_input}" target="_blank">Поиск в архивах</a></div>""",
                unsafe_allow_html=True)

# --- МОДУЛЬ 3: ТЕЛЕФОН ---
elif menu == "📞 Телефонный модуль (Поиск по телефону)":
    st.header("📞 Глобальный поиск по СНГ (RU/UA/BY)")
    
    phone_input = st.text_input("Введите номер (например: 7999..., 380..., 375...):", placeholder="79001112233")
    
    if st.button("ЗАПУСТИТЬ АНАЛИЗ"):
        if not phone_input:
            st.error("Ошибка: Номер не введен.")
        else:
            # Очистка номера
            clean_num = "".join(filter(str.isdigit, phone_input))
            
            st.subheader(f"📊 Досье на номер: +{clean_num}")
            
            # Логика определения страны
            country_info = "Неизвестный регион"
            links = []
            
            # Базовые ссылки (универсальные)
            links.append(f"[💬 Проверить WhatsApp](https://wa.me/{clean_num})")
            links.append(f"[🔵 Проверить Telegram](https://t.me/+{clean_num})")
            links.append(f"[🔍 Поиск в Google (упоминания)](https://www.google.com/search?q=%22{clean_num}%22)")

            if clean_num.startswith("7"):
                country_info = "🇷🇺 Россия"
                links.append(f"[🏢 Проверка оператора (Mtt.ru)](https://num.mtt.ru/search/{clean_num})")
                links.append(f"[💬 Поиск в Viber](viber://chat?number={clean_num})")
                links.append(f"[🔎 Проверить на ТелПоиск (РФ)](https://telpoisk.com/number/{clean_num})")
            
            elif clean_num.startswith("380"):
                country_info = "🇺🇦 Украина"
                links.append(f"[⚡ Телефонный справочник (UA)](https://nomer-telefona.com.ua/nomer/{clean_num})")
                links.append(f"[🔎 Кто звонил (UA)](https://ktodzvoniv.com.ua/number/{clean_num})")
                links.append(f"[💬 Проверить Viber](viber://chat?number={clean_num})")
            
            elif clean_num.startswith("375"):
                country_info = "🇧🇾 Беларусь"
                links.append(f"[🏢 Операторы Беларуси (A1/MTS/Life)](https://reytar.by/phone/{clean_num})")
                links.append(f"[🔎 Поиск по объявлениям (BY)](https://www.google.com/search?q=site:kufar.by+%22{clean_num}%22)")
            
            # Вывод карточки
            st.info(f"📍 Определена локация: **{country_info}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📱 Мессенджеры и связь")
                for link in links[:4]: st.markdown(f"- {link}")
            
            with col2:
                st.markdown("#### 🏢 Региональные базы")
                for link in links[4:]: st.markdown(f"- {link}")

            st.divider()
            st.caption("Совет: Если номер не пробивается, попробуйте поискать его в формате с пробелами или тире через Google.")
# --- МОДУЛЬ 4: NICKNAME ---
# --- МОДУЛЬ 4: NICKNAME (EXTENDED v4.9) ---
elif menu == "🌐 Nickname (Поиск по никнейму)":
    st.header("🌐 Глобальный поиск по Nickname")
    st.info("Система сканирует наличие публичных профилей по цифровому следу.")

    username = st.text_input("Введите никнейм (без @):", placeholder="nekrasova101").strip().replace(" ", "")

    if st.button("ЗАПУСТИТЬ ГЛОБАЛЬНЫЙ СКАНЕР"):
        if not username:
            st.error("Ошибка: Никнейм не введен.")
        else:
            # Словарь площадок: Название -> Шаблон ссылки
            targets = {
                "Telegram": f"https://t.me/{username}",
                "Twitter (X)": f"https://twitter.com/{username}",
                "Instagram": f"https://www.instagram.com/{username}/",
                "VK (ВКонтакте)": f"https://vk.com/{username}",
                "OK (Одноклассники)": f"https://ok.ru/profile/{username}",
                "TikTok": f"https://www.tiktok.com/@{username}",
                "GitHub": f"https://github.com/{username}",
                "YouTube": f"https://www.youtube.com/@{username}",
                "Pinterest": f"https://www.pinterest.com/{username}/",
                "Reddit": f"https://www.reddit.com/user/{username}"
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

            st.subheader(f"🔍 Результаты сканирования для @{username}")

            # Создаем колонки для вывода
            col_res1, col_res2 = st.columns(2)

            count = 0
            for name, url in targets.items():
                try:
                    # Быстрая проверка статус-кода
                    res = requests.get(url, headers=headers, timeout=5, allow_redirects=True)

                    # Простая логика: если 200 OK, значит страница существует
                    if res.status_code == 200:
                        # Дополнительная проверка, чтобы не ловить "Page Not Found" страницы
                        if "not found" not in res.text.lower() and "404" not in res.text:
                            target_col = col_res1 if count % 2 == 0 else col_res2
                            with target_col:
                                st.markdown(f"""<div class="data-card" style="border-left: 5px solid #58a6ff; padding: 10px;">
                                    <b>✅ {name}</b><br>
                                    <a class="card-link" href="{url}" target="_blank">Перейти в профиль</a>
                                </div>""", unsafe_allow_html=True)
                            count += 1
                except:
                    pass

            if count == 0:
                st.warning("Активных публичных совпадений не обнаружено. Попробуйте другой никнейм.")

            st.divider()
            st.subheader("📞 Мессенджеры (Прямая связь)")
            st.info("В WhatsApp и Viber поиск идет по номеру. Если ник совпадает с ID, проверьте ссылки:")
            st.markdown(
                f"[Проверить WhatsApp](https://wa.me/{username}) | [Проверить Telegram](https://t.me/{username})")

# --- МОДУЛЬ 5: VISUAL ID (OPENCV DNN NEURAL ENGINE v4.7) ---
elif menu == "👁 Visual ID (Лицо)":
    st.header("👁 Идентификация по лицу (Neural Vision Engine)")
    t_web, t_local = st.tabs(["🌐 Web-поиск", "🖥 Локальный нейросетевой сканер"])

    with t_web:
        st.markdown(
            f"""<div class="data-card">🤖 <b>FaceCheck.ID</b><br><a class="card-link" href="https://facecheck.id/" target="_blank">Найти профили в соцсетях</a></div>""",
            unsafe_allow_html=True)

    with t_local:
        face_file = st.file_uploader("Загрузите фото для захвата лиц (даже скриншот):", type=['jpg', 'jpeg', 'png'])
        if face_file:
            # Читаем изображение через OpenCV
            file_bytes = np.asarray(bytearray(face_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            (h, w) = image.shape[:2]

            # --- ИНИЦИАЛИЗАЦИЯ НЕЙРОСЕТИ DNN ---
            # Эта нейросеть зашита внутри OpenCV, она мощная и не требует MediaPipe
            try:
                # Пытаемся загрузить встроенные модели (они скачиваются один раз при первом запуске)
                prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
                model_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"


                # Функция для безопасного скачивания файлов моделей
                def download_file(url, filename):
                    if not os.path.exists(filename):
                        with st.spinner(f"Загрузка нейросетевой модели {filename}..."):
                            response = requests.get(url)
                            with open(filename, 'wb') as f:
                                f.write(response.content)


                import os

                download_file(prototxt_url, "deploy.prototxt")
                download_file(model_url, "res10_300x300_ssd_iter_140000.caffemodel")

                net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel")
            except Exception as e:
                st.error(f"Ошибка загрузки нейросети: {e}. Проверьте интернет или установите модели вручную.")
                st.stop()

            # Предобработка изображения для нейросети (blob)
            blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

            with st.spinner("Нейросеть DNN сканирует биометрические паттерны..."):
                net.setInput(blob)
                detections = net.forward()

                face_count = 0
                # Проходим по результатам детектирования
                for i in range(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]

                    # Отфильтровываем слабые детекции (порог 0.5)
                    if confidence > 0.5:
                        face_count += 1
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        # Рисуем рамку и процент уверенности
                        text = f"{round(confidence * 100, 2)}%"
                        y = startY - 10 if startY - 10 > 10 else startY + 10
                        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
                        cv2.putText(image, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

                if face_count > 0:
                    st.success(f"✅ ОБЪЕКТ ИДЕНТИФИЦИРОВАН. ОБНАРУЖЕНО ЛИЦ: {face_count}")

                    # Вывод обработанного фото
                    result_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    st.image(result_img, use_container_width=True)

                    # --- СЕКЦИЯ ГЛОБАЛЬНОГО ПОИСКА (ДЕАНОН) ---
                    st.markdown("### 🔍 ГЛОБАЛЬНАЯ ДЕАНОНИМИЗАЦИЯ")
                    st.warning("Внимание: Поиск по соцсетям требует обращения к мировым нейросетевым индексам.")

                    col_link1, col_link2 = st.columns(2)
                    with col_link1:
                        st.markdown(f"""<div class="data-card" style="text-align: center; border: 1px solid #2ea043;">
                                            <span style="font-size: 2em;">🌐</span><br>
                                            <b>FaceCheck.ID</b><br>
                                            <small>Поиск в Instagram, FB, VK, Tinder</small><br><br>
                                            <a href="https://facecheck.id/" target="_blank" style="background: #2ea043; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">ЗАПУСТИТЬ ГЛОБАЛЬНЫЙ ПОИСК</a>
                                        </div>""", unsafe_allow_html=True)

                    with col_link2:
                        st.markdown(f"""<div class="data-card" style="text-align: center; border: 1px solid #58a6ff;">
                                            <span style="font-size: 2em;">👁</span><br>
                                            <b>PimEyes</b><br>
                                            <small>Поиск по новостям, сайтам и статьям</small><br><br>
                                            <a href="https://pimeyes.com/" target="_blank" style="background: #58a6ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">СКАНЕР СМИ И WEB-САЙТОВ</a>
                                        </div>""", unsafe_allow_html=True)
                    st.info(
                        "💡 Лица зафиксированы. Если это скриншот — система 'пробила' защиту. Используйте Web-поиск для деанонимизации.")
                else:
                    st.error(
                        "❌ ОШИБКА: Нейросеть не обнаружила лиц даже в глубоком режиме. Попробуйте фото с лучшим качеством.")
# --- МОДУЛЬ 6: EXIF ---
elif menu == "📸 EXIF Анализ":
    st.header("📸 EXIF/GPS Анализ")
    file = st.file_uploader("Загрузите JPEG:", type=['jpg', 'jpeg'])
    if file:
        img = Image.open(io.BytesIO(file.read()))
        st.image(img, width=400)
        exif = img._getexif()
        if exif:
            tags = {TAGS.get(tag, tag): value for tag, value in exif.items()}
            st.write(f"Устройство: {tags.get('Model', 'N/A')} | Дата: {tags.get('DateTime', 'N/A')}")
            gps = tags.get('GPSInfo')
            if gps:
                lat = get_decimal_from_dms(gps[2], gps[1]);
                lon = get_decimal_from_dms(gps[4], gps[3])
                if lat and lon:
                    st.success(f"📍 GPS: {lat}, {lon}")
                    m = folium.Map(location=[lat, lon], zoom_start=15)
                    folium.Marker([lat, lon]).add_to(m);
                    st_folium(m, width=800, height=450)
