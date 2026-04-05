import streamlit as st
import pandas as pd
import requests
import json
import folium
from PIL import Image
from PIL.ExifTags import TAGS
from streamlit_folium import st_folium
import io
import urllib.parse
import re
import os
import time
import tempfile
import base64
from bs4 import BeautifulSoup

import cloudinary
import cloudinary.uploader

# --- КОНФИГУРАЦИЯ КЛЮЧЕЙ ---
CLOUDINARY_CLOUD_NAME = "de6r8xxfz"
CLOUDINARY_API_KEY = "937144372127992"
CLOUDINARY_API_SECRET = "muV-3Dm-ELpAvCedTp1S9cTmZhQ"
SERPAPI_KEY = "ec8af88c4e5b056bf35d204585889e277ef9888f012cabd0af0862a77e5c8a85"
SERPER_API_KEY = "573a5d39b86737895b6ebbd3cff10c748059d6e6"
FACECHECK_TOKEN = "aFWG7IIwJocmgmiBr15WOMx56YmOPzVHDu3N3JA4hAyw4YzcTONTExukMqSYDETDcQJ31gW5nao="  # Получи бесплатно: https://facecheck.id → войди → API
FACECHECK_TESTING = True  # True = тест (бесплатно, неточно) | False = продакшн (точно, списывает кредиты)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

st.set_page_config(page_title="kaseye", layout="wide", page_icon="🕸️")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e0e6ed; font-family: 'Consolas', monospace; }
    [data-testid="stSidebar"] { background-color: rgba(10, 13, 18, 0.95) !important; border-right: 2px solid #1a202c; }
    .sidebar-title { color: #58a6ff; font-size: 24px; font-weight: 800; text-align: center; margin-bottom: 20px; }
    .stButton>button { 
        width: 100%; background-image: linear-gradient(135deg, #d73a49 0%, #a71a26 100%);
        color: white; border-radius: 4px; font-weight: bold; border: 1px solid #ff7b72; 
        height: 3.5em; text-transform: uppercase; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(215, 58, 73, 0.8); transform: translateY(-2px); }
    .data-card {
        background-color: rgba(16, 20, 27, 0.9); border: 1px solid #1a202c;
        border-radius: 8px; padding: 20px; margin-bottom: 15px;
    }
    .online-indicator { color: #2ea043; font-weight: bold; animation: pulse 2.5s infinite; text-align: center; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# =============================================================
# ВСЕ ФУНКЦИИ — СТРОГО ДО SIDEBAR И МОДУЛЕЙ
# =============================================================

def get_decimal_from_dms(dms, ref):
    try:
        d = float(dms[0]); m = float(dms[1])/60.0; s = float(dms[2])/3600.0
        return -(d+m+s) if ref in ['S', 'W'] else d+m+s
    except:
        return None

def get_address_from_gps(lat, lon):
    try:
        headers = {'User-Agent': 'Kaseye_OSINT_Tool'}
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        response = requests.get(url, headers=headers, timeout=5)
        return response.json().get('display_name', 'Адрес не найден')
    except:
        return "Ошибка геокодирования"

def search_nazk(name):
    results = []
    try:
        for page in range(1, 4):
            url = "https://public-api.nazk.gov.ua/v2/documents/list"
            params = {"query": name, "page": page}
            res = requests.get(url, params=params, timeout=10).json()
            if res.get('error') or not res.get('data'):
                break
            items = res['data']
            if not items:
                break
            results.extend(items)
            if len(items) < 100:
                break
            time.sleep(0.3)
    except Exception as e:
        st.error(f"НАЗК API помилка: {e}")
    return results

def format_nazk_result(doc):
    try:
        data = doc.get('data', {})
        doc_id = doc.get('id', '')
        year = doc.get('declaration_year', '—')
        dec_type_map = {1: "Щорічна", 2: "Перед звільненням", 3: "Після звільнення", 4: "Кандидата"}
        dec_type = dec_type_map.get(doc.get('declaration_type'), '—')
        step1 = data.get('step_1', {}).get('data', {})
        full_name = f"{step1.get('lastname','')} {step1.get('firstname','')} {step1.get('middlename','')}".strip()
        position = doc.get('responsible_position', '—')
        date = doc.get('date', '—')
        link = f"https://declarations.nazk.gov.ua/declaration/{doc_id}/"
        return {
            "id": doc_id,
            "name": full_name,
            "year": year,
            "type": dec_type,
            "position": position,
            "date": date,
            "link": link
        }
    except:
        return None

# =============================================================
# ФУНКЦИИ ПОИСКА ПО ФОТО
# =============================================================

def upload_to_cloudinary(image_bytes):
    """Общая функция загрузки в Cloudinary, возвращает публичный URL"""
    upload_res = cloudinary.uploader.upload(
        image_bytes,
        folder="kaseye_reverse",
        overwrite=True
    )
    return upload_res.get("secure_url")


def search_google_lens(image_bytes):
    """Google Lens через SerpApi — хорошо для общего поиска"""
    results = []
    try:
        image_url = upload_to_cloudinary(image_bytes)
        if not image_url:
            return [{"error": "Не удалось загрузить фото в Cloudinary"}]

        params = {
            "engine": "google_lens",
            "url": image_url,
            "api_key": SERPAPI_KEY,
            "hl": "uk",
            "gl": "ua"
        }
        data = requests.get("https://serpapi.com/search", params=params, timeout=30).json()

        for item in data.get("visual_matches", [])[:20]:
            results.append({
                "title": item.get("title", "Совпадение"),
                "link": item.get("link", "#"),
                "source": "Google Lens",
                "thumbnail": item.get("thumbnail", ""),
                "domain": item.get("source", "")
            })

        for item in data.get("text_results", [])[:5]:
            results.append({
                "title": item.get("title", "Текст на фото"),
                "link": item.get("link", "#"),
                "source": "Google Lens (текст)",
                "thumbnail": "",
                "domain": item.get("domain", "")
            })

        if "search_metadata" in data:
            results.insert(0, {
                "title": "🔗 Открыть полные результаты Google Lens",
                "link": data["search_metadata"].get("google_lens_url", "https://lens.google.com"),
                "source": "Google Lens",
                "thumbnail": "",
                "domain": ""
            })

    except Exception as e:
        results.append({"error": str(e)})

    return results


def search_bing_visual(image_bytes):
    """Bing Visual Search через SerpApi"""
    results = []
    try:
        image_url = upload_to_cloudinary(image_bytes)
        if not image_url:
            return [{"error": "Cloudinary upload failed"}]

        params = {
            "engine": "bing_visual_search",
            "url": image_url,
            "api_key": SERPAPI_KEY,
        }
        data = requests.get("https://serpapi.com/search", params=params, timeout=30).json()

        for item in data.get("visual_results", {}).get("related_images", [])[:15]:
            results.append({
                "title": item.get("name", "Результат Bing"),
                "link": item.get("host_page_url", "#"),
                "source": "Bing Visual Search",
                "thumbnail": item.get("thumbnail", {}).get("url", ""),
                "domain": item.get("website_name", "")
            })

        results.insert(0, {
            "title": "🔗 Открыть полные результаты Bing",
            "link": "https://www.bing.com/visualsearch",
            "source": "Bing Visual Search",
            "thumbnail": "",
            "domain": ""
        })

    except Exception as e:
        results.append({"error": str(e)})

    return results


def search_tineye_api(image_bytes):
    """TinEye — поиск точных копий фото"""
    results = []
    try:
        files = {"image": ("photo.jpg", image_bytes, "image/jpeg")}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.post(
            "https://tineye.com/search",
            files=files,
            headers=headers,
            timeout=30,
            allow_redirects=True
        )
        soup = BeautifulSoup(res.text, "html.parser")
        matches = soup.select(".match-row a, .result-link, a.link")
        for match in matches[:15]:
            href = match.get("href", "")
            title = match.get_text(strip=True)[:80] or "TinEye совпадение"
            if href and "tineye" not in href and href.startswith("http"):
                results.append({
                    "title": title,
                    "link": href,
                    "source": "TinEye",
                    "thumbnail": "",
                    "domain": ""
                })

        results.insert(0, {
            "title": f"🔗 Открыть TinEye (найдено совпадений: {len(results)})",
            "link": res.url,
            "source": "TinEye",
            "thumbnail": "",
            "domain": ""
        })

    except Exception as e:
        results.append({"error": str(e)})

    return results


def search_facecheck(image_bytes):
    """
    FaceCheck.ID — поиск лиц по соцсетям (ВК, ФБ, TikTok, Instagram и др.)
    Официальный API: https://facecheck.id
    FACECHECK_TESTING = True  → бесплатно, неточно, кредиты не списываются
    FACECHECK_TESTING = False → продакшн, точные результаты, списываются кредиты
    """
    results = []
    site = "https://facecheck.id"

    if not FACECHECK_TOKEN:
        return [{"error": "FaceCheck.ID: токен не задан. Вставь FACECHECK_TOKEN в конфиг. Получить: https://facecheck.id → войди → API"}]

    try:
        headers = {"accept": "application/json", "Authorization": FACECHECK_TOKEN}

        # Шаг 1: загрузка фото
        files = {"images": ("photo.jpg", image_bytes, "image/jpeg"), "id_search": (None, "")}
        r1 = requests.post(f"{site}/api/upload_pic", headers=headers, files=files, timeout=30)
        j1 = r1.json()

        if j1.get("error"):
            return [{"error": f"FaceCheck upload: {j1['error']} ({j1.get('code', '')})"}]

        id_search = j1["id_search"]

        # Шаг 2: polling — ждём результаты
        json_data = {
            "id_search": id_search,
            "with_progress": True,
            "status_only": False,
            "demo": FACECHECK_TESTING
        }

        while True:
            r2 = requests.post(f"{site}/api/search", headers=headers, json=json_data, timeout=30)
            j2 = r2.json()

            if j2.get("error"):
                return [{"error": f"FaceCheck search: {j2['error']} ({j2.get('code', '')})"}]

            if j2.get("output"):
                break

            time.sleep(1)

        items = j2["output"]["items"]

        for item in items[:15]:
            url = item.get("url", "#")
            score = item.get("score", 0)
            b64 = item.get("base64", "")
            thumbnail = f"data:image/jpeg;base64,{b64}" if b64 else ""

            # Пропускаємо результати з дуже низьким score
            if score < 45:
                continue

            domain = ""
            for sn in ["instagram", "facebook", "vk.com", "tiktok", "twitter", "ok.ru",
                       "linkedin", "youtube", "telegram", "pinterest"]:
                if sn in url.lower():
                    domain = sn
                    break

            # Чистий title без HTML тегів
            clean_url = re.sub(r'<[^>]+>', '', url)
            title = f"Совпадение {score:.0f}% — {domain or clean_url[:60]}"

            results.append({
                "title": title,
                "link": url,
                "source": "FaceCheck.ID",
                "thumbnail": thumbnail,
                "domain": domain,
                "score": score
            })

        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        results.insert(0, {
            "title": f"🔗 Открыть FaceCheck.ID (найдено: {len(results)} совпадений)",
            "link": f"https://facecheck.id/#search={id_search}",
            "source": "FaceCheck.ID",
            "thumbnail": "",
            "domain": ""
        })

    except Exception as e:
        results.append({"error": str(e)})

    return results

# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:
    st.markdown("<div class='sidebar-title'>KASEYE 🕸️</div>", unsafe_allow_html=True)
    st.markdown("<p class='online-indicator'>● SYSTEM ONLINE</p>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("Возможности:", [
        "👤 Розыск (По ФИО)",
        "👁 Поиск по фото (По фото)",
        "📸 EXIF Анализ",
        "🚗 Авто (Номера / VIN)",
        "🌐 Nickname (Социальный след)",
        "📧 Email (Утечки и профили)",
        "📞 Телефон (Номер)",
    ])
    st.divider()
    st.caption("")

# =============================================================
# МОДУЛЬ 1: ФИО
# =============================================================

if menu == "👤 Розыск (По ФИО)":
    st.header("👤 Поиск по ФИО (Deep Dorking)")

    col1, col2 = st.columns([3, 1])
    with col1:
        name = st.text_input("Введите ФИО:", placeholder="Іваненко Іван Іванович")
    with col2:
        search_depth = st.selectbox("Глубина:", ["Быстро (1 стр)", "Средне (3 стр)", "Подробно (5 стр)"])

    depth_map = {"Быстро (1 стр)": 1, "Средне (3 стр)": 3, "Подробно (5 стр)": 5}
    pages = depth_map[search_depth]

    DORK_TEMPLATES = [
        '"{name}"',
        '"{name}" site:facebook.com OR site:vk.com OR site:instagram.com',
        '"{name}" site:linkedin.com',
        '"{name}" filetype:pdf OR filetype:doc OR filetype:docx',
        '"{name}" статья OR інтерв\'ю OR біографія',
        '"{name}" site:youtube.com',
        '"{name}" site:*.ua',
        '"{name}" новини OR скандал OR суд OR вирок',
        '"{name}" site:prozorro.gov.ua',
        '"{name}" site:declarations.nazk.gov.ua',
        '"{name}" site:youcontrol.com.ua OR site:opendatabot.ua',
        '"{name}" site:court.gov.ua OR site:reyestr.court.gov.ua',
    ]

    if name and st.button("🚀 НАЧАТЬ ПОИСК"):
        all_results = {}

        tab1, tab2, tab3 = st.tabs(["🌐 Веб-поиск", "🇺🇦 Реестры Украины", "📊 Экспорт"])

        with tab1:
            progress = st.progress(0)
            status = st.empty()
            total_queries = len(DORK_TEMPLATES)

            for i, template in enumerate(DORK_TEMPLATES):
                query = template.format(name=name)
                status.text(f"[{i+1}/{total_queries}] {query[:60]}...")

                try:
                    for page in range(1, pages + 1):
                        payload = json.dumps({
                            "q": query,
                            "gl": "ua",
                            "hl": "uk",
                            "page": page,
                            "num": 10
                        })
                        headers = {
                            'X-API-KEY': SERPER_API_KEY,
                            'Content-Type': 'application/json'
                        }
                        res = requests.post(
                            "https://google.serper.dev/search",
                            headers=headers,
                            data=payload
                        ).json()

                        for item in res.get('organic', []):
                            url = item.get('link')
                            if url and url not in all_results:
                                all_results[url] = {
                                    **item,
                                    'query': query,
                                    'category': ''
                                }

                        time.sleep(0.3)
                except Exception as e:
                    st.warning(f"Ошибка: {e}")

                progress.progress((i + 1) / total_queries)

            status.success(f"✅ Найдено уникальных результатов: {len(all_results)}")
            progress.empty()

            def categorize(url):
                url = url.lower()
                if any(s in url for s in ["facebook", "vk.com", "instagram", "linkedin", "youtube", "tiktok", "twitter", "t.me"]):
                    return "📱 Соцсети"
                if any(s in url for s in ["prozorro", "nazk", "declarations", "court.gov", "nabu", "sap.gov", "minjust", "youcontrol", "opendatabot"]):
                    return "🇺🇦 Реестры"
                if any(s in url for s in [".pdf", ".doc", ".docx", ".xls"]):
                    return "📄 Документы"
                if any(s in url for s in ["news", "novosti", "новини", "укрінформ", "rbc", "ria", "unian", "pravda", "liga", "nv.ua"]):
                    return "📰 Новости"
                return "🌐 Веб"

            for url, item in all_results.items():
                item['category'] = categorize(url)

            categories_order = ["📱 Соцсети", "🇺🇦 Реестры", "📄 Документы", "📰 Новости", "🌐 Веб"]

            for cat in categories_order:
                bucket = [r for r in all_results.values() if r['category'] == cat]
                if not bucket:
                    continue
                with st.expander(f"{cat} — {len(bucket)} результатов", expanded=True):
                    for item in bucket:
                        st.markdown(f"""
                        <div class="data-card">
                            <small style="color:#8b949e">🔎 {item.get('query','')}</small><br>
                            <b>{item.get('title','Без названия')}</b><br>
                            <small style="color:#aaa">{item.get('snippet','')[:200]}</small><br>
                            <a href="{item.get('link')}" target="_blank" 
                               style="color:#58a6ff">→ Открыть источник</a>
                        </div>
                        """, unsafe_allow_html=True)

        with tab2:
            st.subheader("🇺🇦 Українські реєстри")
            st.markdown("### 🏛️ НАЗК — Декларації (прямий API)")

            with st.spinner("Пошук декларацій у НАЗК..."):
                nazk_results = search_nazk(name)

            if nazk_results:
                st.success(f"✅ Знайдено декларацій: {len(nazk_results)}")
                for doc in nazk_results:
                    parsed = format_nazk_result(doc)
                    if not parsed:
                        continue
                    st.markdown(f"""
                    <div class="data-card" style="border-left: 4px solid #f0a500;">
                        <b>📄 {parsed['type']} декларація — {parsed['year']} рік</b><br>
                        <b>👤 {parsed['name']}</b><br>
                        🏢 <small>{parsed['position']}</small><br>
                        📅 <small>Подана: {parsed['date']}</small><br>
                        <a href="{parsed['link']}" target="_blank" style="color:#58a6ff">
                            → Відкрити декларацію
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    all_results[parsed['link']] = {
                        'title': f"НАЗК: {parsed['name']} ({parsed['year']})",
                        'link': parsed['link'],
                        'snippet': f"{parsed['type']} | {parsed['position']} | {parsed['date']}",
                        'query': 'НАЗК API',
                        'category': '🇺🇦 Реестры'
                    }
            else:
                st.warning("Декларацій не знайдено")

            st.divider()
            st.markdown("### 🔗 Інші реєстри (відкриваються в браузері)")

            encoded_name = urllib.parse.quote(name)

            OTHER_REGISTRIES = [
                {
                    "name": "Prozorro — тендери",
                    "url": f"https://prozorro.gov.ua/search/?q={encoded_name}",
                    "icon": "📋",
                    "works": True
                },
                {
                    "name": "Судовий реєстр",
                    "url": f"https://reyestr.court.gov.ua/search#{urllib.parse.quote(name)}",
                    "icon": "⚖️",
                    "works": True
                },
                {
                    "name": "ЄДРПОУ — Мін'юст",
                    "url": f"https://usr.minjust.gov.ua/content/free-search?query={encoded_name}",
                    "icon": "🏢",
                    "works": True
                },
                {
                    "name": "Реєстр боржників",
                    "url": f"https://erb.minjust.gov.ua/#/search-debtors?query={encoded_name}",
                    "icon": "💸",
                    "works": True
                },
                {
                    "name": "YouControl (потрібен акаунт)",
                    "url": f"https://youcontrol.com.ua/search/?country=1&q={encoded_name}",
                    "icon": "🔍",
                    "works": False
                },
                {
                    "name": "OpenDataBot (потрібен акаунт)",
                    "url": f"https://opendatabot.ua/search?q={encoded_name}",
                    "icon": "🤖",
                    "works": False
                },
            ]

            cols = st.columns(2)
            for idx, reg in enumerate(OTHER_REGISTRIES):
                with cols[idx % 2]:
                    border_color = "#2ea043" if reg["works"] else "#6e7681"
                    badge = "" if reg["works"] else " ⚠️ потрібна авторизація"
                    st.markdown(f"""
                    <div class="data-card" style="text-align:center; border-left: 4px solid {border_color};">
                        <div style="font-size:28px">{reg['icon']}</div>
                        <b>{reg['name']}</b>
                        <small style="color:#f0a500">{badge}</small><br><br>
                        <a href="{reg['url']}" target="_blank"
                           style="background:#1f6feb; color:white; padding:8px 18px; 
                                  border-radius:5px; text-decoration:none; font-weight:bold;">
                            🔍 Відкрити
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()
            st.subheader("🔎 Результаты из гос. реестров (через веб-поиск)")
            registry_results = {
                url: item for url, item in all_results.items()
                if item.get('category') == "🇺🇦 Реестры" and item.get('query') != 'НАЗК API'
            }
            if registry_results:
                for item in registry_results.values():
                    st.markdown(f"""
                    <div class="data-card" style="border-left: 4px solid #2ea043;">
                        <b>{item.get('title','')}</b><br>
                        <small>{item.get('snippet','')[:250]}</small><br>
                        <a href="{item.get('link')}" target="_blank" style="color:#58a6ff">→ Открыть</a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Окремих результатів з реєстрів через веб-пошук не знайдено")

        with tab3:
            st.subheader("📊 Экспорт результатов")

            if all_results:
                df = pd.DataFrame([
                    {
                        "Категория": item.get('category', ''),
                        "Заголовок": item.get('title', ''),
                        "URL": item.get('link', ''),
                        "Описание": item.get('snippet', ''),
                        "Поисковый запрос": item.get('query', ''),
                    }
                    for item in all_results.values()
                ])

                st.dataframe(df, use_container_width=True)

                col_csv, col_json = st.columns(2)
                with col_csv:
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="⬇️ Скачать CSV",
                        data=csv_buffer.getvalue().encode('utf-8-sig'),
                        file_name=f"osint_{name.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                with col_json:
                    json_data = json.dumps(
                        list(all_results.values()),
                        ensure_ascii=False,
                        indent=2
                    )
                    st.download_button(
                        label="⬇️ Скачать JSON",
                        data=json_data.encode('utf-8'),
                        file_name=f"osint_{name.replace(' ', '_')}.json",
                        mime="application/json"
                    )

                st.caption(f"Всего записей: {len(df)}")
            else:
                st.warning("Сначала выполните поиск")

# =============================================================
# МОДУЛЬ 2: VISUAL ID
# =============================================================

elif menu == "👁 Поиск по фото (По фото)":
    st.header("👁 Visual ID: Поиск аккаунтов по фото")

    file = st.file_uploader("Загрузите фото лица:", type=['jpg', 'jpeg', 'png'])

    if file:
        col_img, col_info = st.columns([1, 2])

        with col_img:
            st.image(file, caption="Объект поиска", use_column_width=True)

        with col_info:
            st.markdown("""
            <div class="data-card" style="border-left: 4px solid #58a6ff;">
                <b>🎯 Что ищет каждый движок:</b><br><br>
                🟣 <b>FaceCheck.ID</b> — лучший для поиска аккаунтов: ВК, ФБ, TikTok, Instagram, Twitter<br>
                🔵 <b>Google Lens</b> — общий поиск, новости, сайты<br>
                🟡 <b>Bing Visual</b> — дополнительные совпадения<br>
                🔴 <b>TinEye</b> — точные копии фото на других сайтах<br><br>
                <small style="color:#8b949e">⏱ FaceCheck ~20-40 сек | остальные ~5-15 сек</small>
            </div>
            """, unsafe_allow_html=True)

        city_input = st.text_input(
            "🏙️ Місто (необов'язково):",
            placeholder="Київ, Харків, Одеса...",
            help="Якщо вказати місто — буде додатковий пошук по Facebook через Google"
        )

        engine_choice = st.multiselect(
            "Выбери движки для поиска:",
            ["FaceCheck.ID (соцсети)", "Google Lens", "Bing Visual Search", "TinEye"],
            default=["FaceCheck.ID (соцсети)", "Google Lens"]
        )

        if "FaceCheck.ID (соцсети)" in engine_choice and not FACECHECK_TOKEN:
            st.warning(
                "⚠️ **FaceCheck.ID требует API токен.**\n\n"
                "**Как получить (бесплатно):**\n"
                "1. Зайди на [facecheck.id](https://facecheck.id) и зарегистрируйся\n"
                "2. Перейди в раздел **API** в личном кабинете\n"
                "3. Скопируй токен и вставь в `app.py` строку: `FACECHECK_TOKEN = \"вставь_сюда\"`"
            )

        if st.button("🚀 ЗАПУСТИТЬ ПОИСК"):
            image_bytes = file.getvalue()

            engine_map = {
                "FaceCheck.ID (соцсети)": search_facecheck,
                "Google Lens": search_google_lens,
                "Bing Visual Search": search_bing_visual,
                "TinEye": search_tineye_api,
            }

            all_results = []

            for engine_name in engine_choice:
                with st.spinner(f"🔍 Ищем через {engine_name}..."):
                    res = engine_map[engine_name](image_bytes)
                    valid = [r for r in res if not r.get("error")]
                    errors = [r for r in res if r.get("error")]

                    if valid:
                        all_results.extend(valid)
                        st.success(f"✅ {engine_name}: найдено {len(valid)} результатов")
                    if errors:
                        for err in errors:
                            st.error(f"⚠️ {engine_name}: {err['error']}")

            # --- Фільтрація по місту ---
            city = city_input.strip()

            def city_matches(item, city):
                """Перевіряє чи згадується місто в будь-якому полі результату"""
                if not city:
                    return True
                city_lower = city.lower()
                haystack = " ".join([
                    item.get("title", ""),
                    item.get("snippet", ""),
                    item.get("link", ""),
                    item.get("domain", ""),
                ]).lower()
                return city_lower in haystack

            if city:
                before = len(all_results)
                all_results = [r for r in all_results if city_matches(r, city)]
                filtered_out = before - len(all_results)
                if filtered_out > 0:
                    st.info(f"🏙️ Фільтр міста «{city}»: приховано {filtered_out} результатів без згадки міста")

            if all_results:
                st.divider()
                city_label = f" — місто «{city}»" if city else ""
                st.markdown(f"### 📊 Результати{city_label}")

                source_colors = {
                    "FaceCheck.ID": "#9b59b6",
                    "Google Lens": "#4285F4",
                    "Google Lens (текст)": "#34A853",
                    "Bing Visual Search": "#FFB900",
                    "TinEye": "#d73a49",
                }

                social_icons = {
                    "instagram": "📸 Instagram",
                    "facebook": "🔵 Facebook",
                    "vk.com": "💙 ВКонтакте",
                    "tiktok": "🎵 TikTok",
                    "twitter": "🐦 Twitter/X",
                    "ok.ru": "🟠 Одноклассники",
                    "linkedin": "💼 LinkedIn",
                    "youtube": "▶️ YouTube",
                    "telegram": "✈️ Telegram",
                    "pinterest": "📌 Pinterest",
                }

                # --- 1. Акаунти в соцмережах від FaceCheck ---
                face_results = [
                    r for r in all_results
                    if r.get("source") == "FaceCheck.ID"
                    and r.get("domain")
                    and not re.search(r'<[^>]+>', r.get("link", ""))
                    and r.get("link", "").startswith("http")
                ]
                if face_results:
                    st.markdown("#### 👤 Знайдені акаунти в соцмережах (FaceCheck.ID)")
                    for item in face_results:
                        domain = item.get("domain", "")
                        sn_label = social_icons.get(domain, f"🌐 {domain}")
                        score = item.get("score", 0)
                        score_color = "#2ea043" if score > 70 else "#f0a500" if score > 50 else "#8b949e"
                        clean_link = item.get('link', '#')

                        st.markdown(f"""
                        <div class="data-card" style="border-left: 5px solid #9b59b6; display:flex; align-items:center; gap:15px;">
                            {"<img src='"+item.get('thumbnail','')+"' style='width:80px;height:80px;object-fit:cover;border-radius:50%;flex-shrink:0;border:2px solid #9b59b6'>" if item.get('thumbnail') else "<div style='width:80px;height:80px;border-radius:50%;background:#1a1f27;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:28px'>👤</div>"}
                            <div style="flex:1">
                                <b style="font-size:16px">{sn_label}</b>
                                <span style="float:right; color:{score_color}; font-weight:bold">Збіг: {score:.0f}%</span><br>
                                <small style="color:#8b949e">{clean_link[:65]}...</small><br><br>
                                <a href="{clean_link}" target="_blank"
                                   style="background:#9b59b6; color:white; padding:6px 16px;
                                          border-radius:4px; text-decoration:none; font-weight:bold;">
                                    → Відкрити профіль
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # --- 2. Інші збіги (Google Lens, Bing, TinEye) ---
                other_results = [
                    r for r in all_results
                    if not (r.get("source") == "FaceCheck.ID" and r.get("domain"))
                    and not re.search(r'<[^>]+>', r.get("link", ""))
                    and r.get("link", "#") != "#"
                    and r.get("link", "").startswith("http")
                    and r.get("title")
                    and not re.search(r'<[^>]+>', r.get("title", ""))
                ]
                if other_results:
                    st.markdown("#### 🌐 Інші збіги")
                    for item in other_results:
                        thumbnail = item.get('thumbnail', '')
                        color = source_colors.get(item.get('source', ''), '#58a6ff')
                        source_clean = re.sub(r'<[^>]+>', '', item.get('source', ''))
                        title_clean = re.sub(r'<[^>]+>', '', item.get('title', ''))
                        domain_badge = f"<small style='color:#8b949e'>{item.get('domain','')}</small><br>" if item.get('domain') else ""

                        img_html = ""
                        if thumbnail and thumbnail.startswith("http"):
                            img_html = f"<img src='{thumbnail}' style='width:70px;height:70px;object-fit:cover;border-radius:6px;flex-shrink:0' onerror=\"this.style.display='none'\">"

                        st.markdown(f"""
                        <div class="data-card" style="border-left: 5px solid {color}; display:flex; align-items:center; gap:15px;">
                            {img_html}
                            <div>
                                <small style="color:#8b949e">{source_clean}</small><br>
                                {domain_badge}
                                <b>{title_clean[:80]}</b><br>
                                <a href="{item.get('link','#')}" target="_blank" style="color:#58a6ff">→ Відкрити</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            elif city:
                st.warning(f"😔 По фото не знайдено жодного результату з містом «{city}». Спробуй прибрати фільтр міста або вказати інше місто.")

        # --- Ручные инструменты ---
        st.divider()
        st.markdown("### 🔧 Дополнительные инструменты (вручную)")

        # Скачать фото для ручного поиска
        st.download_button(
            label="⬇️ Скачать фото для ручного поиска",
            data=file.getvalue(),
            file_name="face_search.jpg",
            mime="image/jpeg",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        MANUAL_TOOLS = [
            {
                "name": "PimEyes",
                "desc": "Самый мощный поиск лиц. Платный, но находит всё",
                "url": "https://pimeyes.com/en",
                "color": "#e74c3c",
                "icon": "🔴"
            },
            {
                "name": "Search4Faces — ВКонтакте",
                "desc": "Специализированный поиск по базе ВК",
                "url": "https://search4faces.com/vk/",
                "color": "#2787F5",
                "icon": "💙"
            },
            {
                "name": "Search4Faces — Одноклассники",
                "desc": "Специализированный поиск по базе ОК",
                "url": "https://search4faces.com/ok/",
                "color": "#f97400",
                "icon": "🟠"
            },
            {
                "name": "FaceCheck.ID",
                "desc": "Поиск по всем соцсетям — ФБ, TikTok, Instagram",
                "url": "https://facecheck.id",
                "color": "#9b59b6",
                "icon": "🟣"
            },
        ]

        cols = st.columns(2)
        for idx, tool in enumerate(MANUAL_TOOLS):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="data-card" style="text-align:center; border-left: 4px solid {tool['color']};">
                    <div style="font-size:28px">{tool['icon']}</div>
                    <b>{tool['name']}</b><br>
                    <small style="color:#8b949e">{tool['desc']}</small><br><br>
                    <a href="{tool['url']}" target="_blank"
                       style="background:{tool['color']}; color:white; padding:8px 18px;
                              border-radius:5px; text-decoration:none; font-weight:bold;">
                        🔍 Открыть
                    </a>
                </div>
                """, unsafe_allow_html=True)

# =============================================================
# МОДУЛЬ 3: EXIF
# =============================================================

elif menu == "📸 EXIF Анализ":
    st.header("📸 Глубокий EXIF/GPS Анализ")
    file = st.file_uploader("Загрузите JPEG:", type=['jpg', 'jpeg', 'png'])
    if file:
        img = Image.open(file)
        st.image(img, width=500, caption="Объект")
        t1, t2 = st.tabs(["📂 Локальные метаданные", "☁️ Cloud AI Scan"])
        with t1:
            exif = img._getexif()
            if exif:
                tags = {TAGS.get(tag, tag): value for tag, value in exif.items()}
                st.write("🔍 Технические теги:")
                st.json({k: str(v) for k, v in tags.items() if k != 'GPSInfo'})
                gps = tags.get('GPSInfo')
                if gps:
                    lat = get_decimal_from_dms(gps[2], gps[1])
                    lon = get_decimal_from_dms(gps[4], gps[3])
                    if lat and lon:
                        addr = get_address_from_gps(lat, lon)
                        st.success(f"📍 GPS: {lat}, {lon}")
                        st.info(f"🏠 Адрес: {addr}")
                        m = folium.Map(location=[lat, lon], zoom_start=15)
                        folium.Marker([lat, lon], popup=addr).add_to(m)
                        st_folium(m, width=700, height=400)
            else:
                st.warning("Метаданные не найдены.")
        with t2:
            if st.button("🚀 ЗАПУСТИТЬ ОБЛАЧНОЕ СКАНИРОВАНИЕ"):
                with st.spinner("Анализ в облаке Cloudinary..."):
                    try:
                        res = cloudinary.uploader.upload(file.getvalue(), image_metadata=True)
                        st.success("✅ Анализ завершен")
                        st.json(res.get('image_metadata', {}))
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

# =============================================================
# МОДУЛЬ 4: АВТО
# =============================================================

elif menu == "🚗 Авто (Номера / VIN)":
    st.header("🚗 Идентификация транспортного средства")

    tab_plate, tab_vin = st.tabs(["🔢 Держномер (ГРЗ)", "🔑 VIN-код"])

    # ── ГРЗ ──────────────────────────────────────────────────
    with tab_plate:
        plate = st.text_input("Введите госномер (АА3333АА):", key="plate_input").strip().upper().replace(" ", "")
        if plate:
            st.subheader(f"🔎 Об'єкт: {plate}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="data-card" style="border-left:4px solid #58a6ff;">
                    📑 <b>ТЕХПАСПОРТ</b><br><br>
                    <a href="https://baza-gai.com.ua/nomer/{plate}" target="_blank"
                       style="background:#1f6feb;color:white;padding:8px 16px;border-radius:4px;text-decoration:none;font-weight:bold;">
                        🔍 ХАРАКТЕРИСТИКИ (Baza-GAI)
                    </a>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="data-card" style="border-left:4px solid #f0a500;">
                    👤 <b>ВЛАСНИКИ</b><br><br>
                    <a href="https://opendatabot.ua/auto/{plate}" target="_blank"
                       style="background:#f0a500;color:#000;padding:8px 16px;border-radius:4px;text-decoration:none;font-weight:bold;">
                        📋 ІСТОРІЯ (OpenDataBot)
                    </a>
                </div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("### 🔗 Додаткові джерела")
            extra_cols = st.columns(3)
            extra_sources = [
                ("🚔 ПДД штрафи",  "https://www.mia.gov.ua/",                                    "#d73a49"),
                ("📂 Арешти авто", "https://erb.minjust.gov.ua/#/search-debtors",                "#9b59b6"),
                ("🔍 CarVertical", f"https://www.carvertical.com/ua/check?plate={plate}",         "#2ea043"),
            ]
            for col, (label, url, color) in zip(extra_cols, extra_sources):
                with col:
                    st.markdown(f"""
                    <div class="data-card" style="text-align:center;border-left:4px solid {color};">
                        <b>{label}</b><br><br>
                        <a href="{url}" target="_blank"
                           style="background:{color};color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-weight:bold;">
                            → Відкрити
                        </a>
                    </div>""", unsafe_allow_html=True)

    # ── VIN ──────────────────────────────────────────────────
    with tab_vin:
        vin = st.text_input("Введите VIN-код (17 символів):", key="vin_input").strip().upper().replace(" ", "")
        if vin:
            if len(vin) != 17:
                st.warning(f"⚠️ VIN має бути 17 символів, зараз: {len(vin)}")
            else:
                st.subheader(f"🔎 VIN: {vin}")
                with st.spinner("🔍 Шукаємо інформацію по VIN..."):
                    try:
                        payload = json.dumps({
                            "q": vin,
                            "gl": "ua",
                            "hl": "uk",
                            "num": 10
                        })
                        headers_vin = {
                            'X-API-KEY': SERPER_API_KEY,
                            'Content-Type': 'application/json'
                        }
                        vin_res = requests.post(
                            "https://google.serper.dev/search",
                            headers=headers_vin,
                            data=payload,
                            timeout=15
                        ).json()

                        results_vin = vin_res.get('organic', [])[:6]

                        if results_vin:
                            st.success(f"✅ Знайдено {len(results_vin)} результатів")
                            for item in results_vin:
                                title = item.get('title', 'Без назви')
                                link = item.get('link', '#')
                                snippet = item.get('snippet', '')
                                domain = link.split('/')[2] if link.startswith('http') else ''

                                # Визначаємо колір по домену
                                color = "#58a6ff"
                                if any(x in domain for x in ["carvertical", "carfax", "autocheck"]):
                                    color = "#2ea043"
                                elif any(x in domain for x in ["gov", "mia", "mvs"]):
                                    color = "#d73a49"
                                elif any(x in domain for x in ["opendatabot", "baza-gai"]):
                                    color = "#f0a500"

                                st.markdown(f"""
                                <div class="data-card" style="border-left:4px solid {color};">
                                    <small style="color:#8b949e">🌐 {domain}</small><br>
                                    <b>{title}</b><br>
                                    <small style="color:#aaa">{snippet[:180]}</small><br><br>
                                    <a href="{link}" target="_blank"
                                       style="background:{color};color:white;padding:6px 16px;
                                              border-radius:4px;text-decoration:none;font-weight:bold;">
                                        → Відкрити
                                    </a>
                                </div>""", unsafe_allow_html=True)
                        else:
                            st.warning("Нічого не знайдено по цьому VIN")

                    except Exception as e:
                        st.error(f"Помилка пошуку: {e}")

# =============================================================
# МОДУЛЬ 5: NICKNAME
# =============================================================

elif menu == "🌐 Nickname (Социальный след)":
    st.header("🌐 Поиск по Nickname")
    nick = st.text_input("Введите никнейм (без @):").strip()
    if nick:
        st.subheader(f"🔍 След ника: {nick}")

        NICK_SOURCES = [
            ("📸 Instagram",      f"https://instagram.com/{nick}",                        "#E1306C"),
            ("🎵 TikTok",         f"https://www.tiktok.com/@{nick}",                      "#010101"),
            ("🐦 Twitter/X",      f"https://x.com/{nick}",                                "#1DA1F2"),
            ("💼 LinkedIn",       f"https://linkedin.com/in/{nick}",                      "#0077B5"),
            ("▶️ YouTube",        f"https://youtube.com/@{nick}",                         "#FF0000"),
            ("🐙 GitHub",         f"https://github.com/{nick}",                           "#6e40c9"),
            ("🎮 Steam",          f"https://steamcommunity.com/id/{nick}",                "#1b2838"),
            ("🟠 Reddit",         f"https://reddit.com/user/{nick}",                      "#FF4500"),
            ("📌 Pinterest",      f"https://pinterest.com/{nick}",                        "#E60023"),
            ("🎵 Spotify",        f"https://open.spotify.com/user/{nick}",                "#1DB954"),
            ("💬 Telegram",       f"https://t.me/{nick}",                                 "#0088cc"),
            ("🔵 Facebook",       f"https://facebook.com/{nick}",                         "#1877F2"),
            ("💙 ВКонтакте",      f"https://vk.com/{nick}",                               "#2787F5"),
            ("🟠 Одноклассники",  f"https://ok.ru/{nick}",                               "#f97400"),
        ]

        cols = st.columns(2)
        for idx, (label, url, color) in enumerate(NICK_SOURCES):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="data-card" style="border-left:4px solid {color}; display:flex; align-items:center; justify-content:space-between;">
                    <b>{label}</b>
                    <a href="{url}" target="_blank"
                       style="background:{color};color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-weight:bold;white-space:nowrap;">
                        → Перевірити
                    </a>
                </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🌐 Агрегатори")
        agg_cols = st.columns(2)
        aggregators = [
            ("🔎 Namecheckr",  f"https://www.namecheckr.com/",              "#58a6ff"),
            ("🕵️ Sherlock",    f"https://sherlock-project.github.io/",      "#d73a49"),
            ("🌍 WhatsMyName", f"https://whatsmyname.app/?q={nick}",        "#2ea043"),
            ("📊 NameCheck",   f"https://namecheck.com/{nick}",             "#f0a500"),
        ]
        for idx, (label, url, color) in enumerate(aggregators):
            with agg_cols[idx % 2]:
                st.markdown(f"""
                <div class="data-card" style="border-left:4px solid {color}; display:flex; align-items:center; justify-content:space-between;">
                    <b>{label}</b>
                    <a href="{url}" target="_blank"
                       style="background:{color};color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-weight:bold;">
                        → Відкрити
                    </a>
                </div>""", unsafe_allow_html=True)

# =============================================================
# МОДУЛЬ 6: EMAIL
# =============================================================

elif menu == "📧 Email (Утечки и профили)":
    st.header("📧 Разведка по Email")
    email = st.text_input("Введите адрес (example@gmail.com):").strip()
    if email:
        st.subheader(f"📊 Анализ объекта: {email}")
        u_nick = email.split('@')[0]

        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown("### 🔍 Перевірка акаунтів")
            sources_left = [
                ("🌐 EPIOS / Google", f"https://www.google.com/search?q=site:epios.com+%22{email}%22",
                 "Шукає фото і ім'я власника через індексацію Google.", "#58a6ff"),
                ("🕵️ Sherlock Web", f"https://www.google.com/search?q=%22{u_nick}%22+social+networks",
                 f"Шукає нік {u_nick} на всіх форумах і соцмережах.", "#9b59b6"),
                ("🔵 Facebook пошук", f"https://www.facebook.com/search/top?q={email}",
                 "Прямий пошук по email у Facebook.", "#1877F2"),
                ("💼 LinkedIn пошук", f"https://www.linkedin.com/search/results/all/?keywords={email}",
                 "Пошук профілю на LinkedIn.", "#0077B5"),
            ]
            for label, url, desc, color in sources_left:
                st.markdown(f"""
                <div class="data-card" style="border-left:4px solid {color};">
                    <b>{label}</b><br>
                    <small style="color:#8b949e">{desc}</small><br><br>
                    <a href="{url}" target="_blank"
                       style="background:{color};color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-weight:bold;">
                        → Відкрити
                    </a>
                </div>""", unsafe_allow_html=True)

        with col_2:
            st.markdown("### 🚨 Витоки і Бази")
            sources_right = [
                ("🔴 HaveIBeenPwned", f"https://haveibeenpwned.com/account/{email}",
                 "Де злито пошту — найбільша база витоків.", "#d73a49"),
                ("🕳️ IntelX (Даркнет)", f"https://intelx.io/?s={email}",
                 "Пошук в дампах і даркнеті.", "#6e40c9"),
                ("📬 LeakCheck", f"https://leakcheck.io/?query={email}",
                 "Перевірка пошти в базах паролів.", "#f0a500"),
                ("🔍 Epieos", f"https://epieos.com/?q={email}",
                 "Google ID, Gravatar, соцмережі по email.", "#2ea043"),
            ]
            for label, url, desc, color in sources_right:
                st.markdown(f"""
                <div class="data-card" style="border-left:4px solid {color};">
                    <b>{label}</b><br>
                    <small style="color:#8b949e">{desc}</small><br><br>
                    <a href="{url}" target="_blank"
                       style="background:{color};color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-weight:bold;">
                        → Відкрити
                    </a>
                </div>""", unsafe_allow_html=True)

# =============================================================
# МОДУЛЬ 7: ТЕЛЕФОН
# =============================================================

elif menu == "📞 Телефон (Номер)":
    st.header("📞 Активний OSINT-пробив номера")
    phone = st.text_input("Введите номер (380...):").strip()

    if phone:
        num = "".join(filter(str.isdigit, phone))
        st.subheader(f"📊 Об'єкт: +{num}")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### 👤 Імена і Теги")
            phone_left = [
                ("📱 GetContact", f"https://www.getcontact.com/en/search?q={num}",
                 "Головний шанс отримати 1-2 реальних імені або нікнейму.", "#00c853"),
                ("📞 TrueCaller", f"https://www.truecaller.com/search/ua/{num}",
                 "Пошук по базі Caller ID.", "#3399FF"),
                ("🔍 Google Dork", f"https://www.google.com/search?q=%22{num}%22+OR+%22+{num[:3]}+{num[3:6]}+{num[6:]}%22",
                 "Пошук всіх згадок номера в інтернеті.", "#58a6ff"),
            ]
            for label, url, desc, color in phone_left:
                st.markdown(f"""
                <div class="data-card" style="border-left:4px solid {color};">
                    <b>{label}</b><br>
                    <small style="color:#8b949e">{desc}</small><br><br>
                    <a href="{url}" target="_blank"
                       style="background:{color};color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-weight:bold;">
                        → Перевірити
                    </a>
                </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("### 📱 Профілі в месенджерах")
            phone_right = [
                ("💬 WhatsApp", f"https://wa.me/{num}",
                 "Якщо акаунт є — побачиш аватарку і час в мережі.", "#25d366"),
                ("✈️ Telegram", f"https://t.me/+{num}",
                 "Прямий перехід до профілю.", "#0088cc"),
                ("📘 Viber", f"viber://chat?number=%2B{num}",
                 "Відкрити чат у Viber.", "#7360f2"),
            ]
            for label, url, desc, color in phone_right:
                st.markdown(f"""
                <div class="data-card" style="border-left:4px solid {color};">
                    <b>{label}</b><br>
                    <small style="color:#8b949e">{desc}</small><br><br>
                    <a href="{url}" target="_blank"
                       style="background:{color};color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-weight:bold;">
                        → Відкрити
                    </a>
                </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🌍 Міжнародні бази")
        intl_cols = st.columns(3)
        intl_sources = [
            ("🔴 NumLookup",  f"https://www.numlookup.com/?number=%2B{num}",  "#d73a49"),
            ("🟡 SpyDialer",  f"https://www.spydialer.com/default.aspx?phone={num}", "#f0a500"),
            ("🟣 CallerID",   f"https://calleridtest.com/lookup?phone={num}",  "#9b59b6"),
        ]
        for col, (label, url, color) in zip(intl_cols, intl_sources):
            with col:
                st.markdown(f"""
                <div class="data-card" style="text-align:center;border-left:4px solid {color};">
                    <b>{label}</b><br><br>
                    <a href="{url}" target="_blank"
                       style="background:{color};color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-weight:bold;">
                        → Відкрити
                    </a>
                </div>""", unsafe_allow_html=True)
