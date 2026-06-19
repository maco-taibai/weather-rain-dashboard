import html
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
CITY_FILE = BASE_DIR / "data" / "china_city_locations.csv"

DEFAULT_CITIES = [
    "上海市",
    "深圳市",
    "大连市",
    "天津市",
    "西安市",
    "无锡市",
    "长沙市",
    "杭州市",
    "成都市",
    "宁波市",
    "苏州市",
    "南京市",
    "青岛市",
    "沈阳市",
    "济南市",
]

MAX_SELECTED_CITIES = 30
HOURS = [f"{hour:02d}" for hour in range(24)]
WEATHER_CACHE_TTL_SECONDS = 60 * 60 * 3

load_dotenv(BASE_DIR / ".env")


def get_secret(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except Exception:
        return None


QWEATHER_API_KEY = get_secret("QWEATHER_API_KEY")
QWEATHER_API_HOST = get_secret("QWEATHER_API_HOST")
WEATHERAPI_KEY = get_secret("WEATHERAPI_KEY")

SOURCE_WEIGHTS = {
    "open_meteo": 4,
    "qweather": 3,
    "weatherapi": 3,
}


def page_config():
    st.set_page_config(
        page_title="城市72小时降雨概率雷达",
        page_icon="🌧️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --sky: #eaf8ff;
            --sky-deep: #58b7ee;
            --panel: rgba(255, 255, 255, 0.86);
            --panel-solid: #ffffff;
            --line: rgba(78, 157, 215, 0.18);
            --text: #17324a;
            --muted: #5f7f98;
            --blue: #1f8ed8;
            --blue-soft: #e5f5ff;
        }

        .stApp {
            background:
                linear-gradient(180deg, #cceeff 0%, #eefaff 42%, #f8fcff 100%);
            color: var(--text);
        }

        .block-container {
            padding-top: 0.75rem;
            padding-bottom: 2rem;
            max-width: 1480px;
        }

        header[data-testid="stHeader"],
        div[data-testid="stHeader"],
        .stApp > header {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        #MainMenu,
        footer,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stDeployButton"],
        .stDeployButton {
            display: none !important;
            visibility: hidden !important;
        }

        [data-testid="stAppViewBlockContainer"] {
            padding-top: 0.75rem;
        }

        .dashboard-header {
            border: 1px solid rgba(255, 255, 255, 0.78);
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.88), rgba(225, 246, 255, 0.76));
            border-radius: 8px;
            padding: 18px 22px;
            box-shadow: 0 18px 44px rgba(57, 139, 190, 0.16);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 12px;
        }

        .dashboard-title {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: 0;
            color: #143a56;
        }

        .dashboard-subtitle {
            margin-top: 6px;
            color: #6389a5;
            font-size: 14px;
        }

        .service-label {
            color: #2878b5;
            text-align: right;
            font-size: 15px;
            font-weight: 700;
        }

        .section-panel {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 14px 34px rgba(67, 145, 190, 0.12);
        }

        .operation-panel {
            border: 1px solid rgba(255, 255, 255, 0.80);
            background: rgba(255, 255, 255, 0.82);
            border-radius: 8px;
            padding: 16px 18px;
            box-shadow: 0 14px 34px rgba(67, 145, 190, 0.12);
            margin-bottom: 12px;
        }

        .operation-block {
            min-height: 116px;
        }

        div[data-testid="stVerticalBlock"]:has(.operation-caption):has(.operation-title) {
            min-height: 134px;
        }

        .operation-title {
            color: #173a56;
            font-size: 16px;
            font-weight: 800;
            margin-bottom: 12px;
            text-align: left;
        }

        .operation-caption {
            color: #6b8ba3;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 6px;
            text-align: left;
        }

        .operation-center {
            text-align: left;
        }

        .operation-center .operation-caption,
        .operation-center .operation-title {
            text-align: left;
        }

        .date-filter-inner {
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
            text-align: left;
        }

        .date-filter-inner .operation-caption,
        .date-filter-inner .operation-title {
            text-align: left;
        }

        .heatmap-panel {
            border: 1px solid rgba(71, 151, 211, 0.18);
            background: rgba(255, 255, 255, 0.90);
            border-radius: 8px;
            padding: 18px;
            box-shadow: 0 18px 42px rgba(67, 145, 190, 0.14);
            margin-bottom: 12px;
        }

        .heatmap-topline {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 10px;
        }

        .heatmap-title {
            color: #173a56;
            font-size: 22px;
            font-weight: 850;
        }

        .heatmap-context {
            color: #6b8ba3;
            font-size: 13px;
            font-weight: 700;
            text-align: right;
        }

        .metric-card {
            border: 1px solid rgba(82, 166, 226, 0.16);
            background: rgba(255, 255, 255, 0.86);
            border-radius: 8px;
            padding: 16px;
            min-height: 104px;
            box-shadow: 0 10px 26px rgba(67, 145, 190, 0.10);
        }

        .metric-label {
            color: #5d7f98;
            font-size: 13px;
            font-weight: 700;
        }

        .metric-value {
            color: #1469a6;
            font-size: 28px;
            font-weight: 800;
            margin-top: 8px;
        }

        .metric-hint {
            color: #83a2b8;
            font-size: 12px;
            margin-top: 4px;
        }

        .city-summary {
            border: 1px solid rgba(61, 154, 221, 0.20);
            background: #f4fbff;
            border-radius: 8px;
            padding: 10px 12px;
            color: #284c66;
            font-size: 14px;
            line-height: 1.5;
            min-height: 48px;
            text-align: left;
        }

        .heatmap-wrap {
            overflow: visible;
            border: 1px solid rgba(72, 151, 211, 0.18);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.72);
            line-height: 0;
            padding-bottom: 8px;
        }

        .rain-table {
            width: 100%;
            min-width: 0;
            border-collapse: separate;
            border-spacing: 0;
            table-layout: fixed;
            font-size: 12px;
            margin: 0;
            line-height: 1.2;
        }

        .heatmap-wrap .rain-table {
            margin-bottom: 0 !important;
        }

        .rain-table th {
            height: 34px;
            color: #36647f;
            background: #eaf7ff;
            border-bottom: 1px solid rgba(76, 158, 217, 0.18);
            font-weight: 700;
            white-space: nowrap;
        }

        .rain-table th.city-head {
            width: 164px;
            text-align: left;
            padding-left: 10px;
        }

        .rain-table td {
            height: 32px;
            text-align: center;
            border-top: 1px solid rgba(76, 158, 217, 0.12);
            border-right: 1px solid rgba(76, 158, 217, 0.10);
            color: #14324a;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: clip;
            position: relative;
        }

        .rain-table td.city-cell {
            text-align: left;
            padding-left: 10px;
            color: #214c68;
            background: #f7fcff;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .city-name {
            color: #1d4865;
        }

        .city-weather {
            color: #6a8ba3;
            font-weight: 700;
            font-size: 11px;
        }

        .rain-cell {
            cursor: default;
            overflow: visible !important;
            z-index: 2;
        }

        .rain-cell::after {
            content: attr(data-tooltip);
            position: absolute;
            left: 50%;
            top: calc(100% + 8px);
            transform: translateX(-50%);
            min-width: 188px;
            max-width: 240px;
            white-space: pre-line;
            text-align: left;
            background: rgba(255, 255, 255, 0.98);
            color: #1d4865;
            border: 1px solid rgba(42, 145, 215, 0.22);
            border-radius: 8px;
            padding: 10px 12px;
            box-shadow: 0 12px 28px rgba(67, 145, 190, 0.22);
            font-size: 12px;
            line-height: 1.55;
            font-weight: 700;
            opacity: 0;
            pointer-events: none;
            z-index: 999;
        }

        .rain-cell:hover::after {
            opacity: 1;
        }

        .rain-cell:hover {
            z-index: 1000;
        }

        div[data-testid="stVerticalBlock"]:has(.heatmap-wrap) {
            padding-bottom: 0 !important;
        }

        div[data-testid="stElementContainer"]:has(.heatmap-wrap) {
            margin-bottom: 0 !important;
        }

        .rain-low { background: #dff7e9; color: #236342 !important; }
        .rain-mid { background: #fff1b8; color: #765b00 !important; }
        .rain-high { background: #ffd0a6; color: #8a3f00 !important; }
        .rain-extreme { background: #ff9f9f; color: #7a1020 !important; }
        .rain-empty { background: #f4f9fc; color: rgba(86, 120, 145, 0.30) !important; }

        .module-title {
            color: #173a56;
            font-size: 14px;
            font-weight: 850;
            margin-bottom: 6px;
            white-space: nowrap;
        }

        .module-subtitle {
            color: #6b8ba3;
            font-size: 11px;
            font-weight: 700;
            margin-top: -2px;
            margin-bottom: 8px;
        }

        .toolbar-label {
            color: #5f7f98;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .heatmap-heading {
            color: #173a56;
            font-size: 18px;
            font-weight: 800;
            margin-top: 4px;
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
        }

        .status-chip {
            border: 1px solid rgba(42, 145, 215, 0.16);
            background: #f3fbff;
            border-radius: 8px;
            padding: 10px 12px;
            min-height: 64px;
        }

        .status-label {
            color: #6b8ba3;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .status-value {
            color: #1469a6;
            font-size: 20px;
            font-weight: 850;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .support-strip {
            display: grid;
            grid-template-columns: minmax(0, 1.55fr) minmax(230px, 0.95fr) minmax(260px, 1.15fr);
            gap: 12px;
            align-items: stretch;
            border: 1px solid rgba(71, 151, 211, 0.16);
            background: rgba(255, 255, 255, 0.76);
            border-radius: 8px;
            padding: 12px 14px;
            box-shadow: 0 10px 26px rgba(67, 145, 190, 0.08);
            margin-top: 10px;
        }

        .support-item {
            min-width: 0;
            border-right: 1px solid rgba(76, 158, 217, 0.14);
            padding-right: 12px;
        }

        .support-item:last-child {
            border-right: none;
            padding-right: 0;
        }

        .rank-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
        }

        .rank-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            max-width: 148px;
            min-height: 28px;
            border: 1px solid rgba(42, 145, 215, 0.16);
            background: #f4fbff;
            border-radius: 999px;
            padding: 4px 9px 4px 5px;
            color: #294f69;
        }

        .rank-badge {
            width: 20px;
            height: 20px;
            border-radius: 999px;
            background: #dff2ff;
            color: #1469a6;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 850;
            flex: 0 0 auto;
        }

        .rank-city {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 12px;
            font-weight: 800;
            min-width: 0;
        }

        .rank-value {
            color: #1469a6;
            font-size: 12px;
            font-weight: 850;
            flex: 0 0 auto;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 7px;
            margin: 0;
            color: #294f69;
            min-height: 22px;
            font-size: 12px;
            font-weight: 700;
        }

        .legend-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 6px 10px;
        }

        .legend-swatch {
            width: 22px;
            height: 11px;
            border-radius: 3px;
            border: 1px solid rgba(255, 255, 255, 0.16);
            flex: 0 0 auto;
        }

        .data-note {
            color: #587a92;
            line-height: 1.55;
            font-size: 12px;
        }

        @media (max-width: 980px) {
            .support-strip {
                grid-template-columns: 1fr;
            }

            .support-item {
                border-right: none;
                border-bottom: 1px solid rgba(76, 158, 217, 0.14);
                padding-right: 0;
                padding-bottom: 10px;
            }

            .support-item:last-child {
                border-bottom: none;
                padding-bottom: 0;
            }
        }

        div[data-testid="stMetric"] {
            background: transparent;
        }

        .stButton > button, div[data-testid="stPopover"] button {
            border-radius: 6px;
            border: 1px solid rgba(42, 145, 215, 0.24);
            background: #e6f5ff;
            color: #1469a6;
            font-weight: 700;
        }

        .stButton > button:hover, div[data-testid="stPopover"] button:hover {
            border-color: rgba(42, 145, 215, 0.52);
            background: #d8f0ff;
            color: #0f5f99;
        }

        div[data-testid="stRadio"] label {
            color: #355f78;
            font-weight: 700;
        }

        div[data-testid="stRadio"] > div {
            justify-content: flex-start;
            padding-left: 0;
        }

        div[data-testid="stRadio"] {
            margin-left: 0;
        }

        div[data-baseweb="radio"] {
            background: #f3fbff;
            border: 1px solid rgba(69, 157, 220, 0.16);
            border-radius: 8px;
            padding: 7px 10px;
        }

        .stTextInput input {
            border-radius: 6px;
        }

        [data-testid="stAlert"] {
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_city_locations():
    if not CITY_FILE.exists():
        return None
    cities = pd.read_csv(CITY_FILE, dtype={"location_id": str})
    required_columns = {"province", "city", "location_id", "lat", "lon"}
    missing_columns = required_columns - set(cities.columns)
    if missing_columns:
        raise ValueError(f"城市配置文件缺少字段：{', '.join(sorted(missing_columns))}")
    cities["city"] = cities["city"].astype(str).str.strip()
    cities["province"] = cities["province"].astype(str).str.strip()
    return cities.drop_duplicates(subset=["city"]).reset_index(drop=True)


def init_session_state(city_df):
    available_cities = city_df["city"].tolist() if city_df is not None else []
    default_available = [city for city in DEFAULT_CITIES if city in available_cities]

    if "selected_cities" not in st.session_state:
        st.session_state["selected_cities"] = default_available or available_cities[: min(15, len(available_cities))]

    if "pending_selected_cities" not in st.session_state:
        st.session_state["pending_selected_cities"] = list(st.session_state["selected_cities"])


def clean_selected_cities(cities, valid_cities):
    seen = set()
    cleaned = []
    for city in cities:
        if city in valid_cities and city not in seen:
            cleaned.append(city)
            seen.add(city)
    return cleaned


def format_city_summary(selected_cities):
    if not selected_cities:
        return "当前城市：0个"
    preview = "、".join(selected_cities[:5])
    suffix = "等" if len(selected_cities) > 5 else ""
    return f"当前城市：{len(selected_cities)}个｜{preview}{suffix}"


def sync_dashboard_cities(cities, valid_cities):
    synced = clean_selected_cities(cities, valid_cities)
    st.session_state["pending_selected_cities"] = synced
    st.session_state["selected_cities"] = synced


def render_city_selector(city_df):
    selected_cities = st.session_state.get("selected_cities", [])
    summary_col, action_col = st.columns([2.2, 1])
    with summary_col:
        st.markdown(f"<div class='city-summary'>{html.escape(format_city_summary(selected_cities))}</div>", unsafe_allow_html=True)

    with action_col:
        if hasattr(st, "popover"):
            selector = st.popover("选择 / 更换城市", use_container_width=True)
        else:
            selector = st.expander("选择 / 更换城市", expanded=False)

    with selector:
        valid_cities = city_df["city"].tolist()
        st.session_state["pending_selected_cities"] = clean_selected_cities(
            st.session_state.get("pending_selected_cities", selected_cities),
            valid_cities,
        )
        city_province_map = city_df.set_index("city")["province"].to_dict()
        pending = clean_selected_cities(st.session_state["pending_selected_cities"], valid_cities)

        st.caption(f"城市库：{city_df['province'].nunique()} 个省级区域，{len(city_df)} 个地级层级城市。已选 {len(pending)}/{MAX_SELECTED_CITIES}。添加或移除后会立即同步看板。")

        keyword = st.text_input("城市名称搜索", placeholder="输入城市名，例如：嘉兴、福州、深圳", key="city_keyword").strip()
        search_results = city_df[city_df["city"].str.contains(keyword, case=False, na=False)] if keyword else city_df.head(0)

        st.markdown("**搜索结果**")
        if keyword and search_results.empty:
            st.info("没有找到匹配的地级城市。")
        elif keyword:
            for _, row in search_results.head(12).iterrows():
                city = row["city"]
                result_cols = st.columns([2.5, 1])
                with result_cols[0]:
                    st.write(f"{city}（{row['province']}）")
                with result_cols[1]:
                    already_selected = city in pending
                    over_limit = len(pending) >= MAX_SELECTED_CITIES and not already_selected
                    button_label = "已选" if already_selected else "添加"
                    if st.button(button_label, key=f"add_search_{city}", disabled=already_selected or over_limit, use_container_width=True):
                        sync_dashboard_cities(pending + [city], valid_cities)
                        st.rerun()

        st.markdown("**已选城市**")
        if not pending:
            st.info("请至少添加一个城市。")
        else:
            for start in range(0, len(pending), 3):
                selected_cols = st.columns(3)
                for col, city in zip(selected_cols, pending[start : start + 3]):
                    with col:
                        label = f"× {city}（{city_province_map.get(city, '')}）"
                        if st.button(label, key=f"remove_pending_{city}", use_container_width=True):
                            sync_dashboard_cities([item for item in pending if item != city], valid_cities)
                            st.rerun()

        st.markdown("**按省份浏览添加**")
        provinces = city_df["province"].dropna().drop_duplicates().tolist()
        browse_province = st.selectbox("选择省份", provinces, key="browse_province", label_visibility="collapsed")
        province_cities = city_df[city_df["province"] == browse_province]["city"].tolist()
        for start in range(0, len(province_cities), 4):
            browse_cols = st.columns(4)
            for col, city in zip(browse_cols, province_cities[start : start + 4]):
                with col:
                    already_selected = city in pending
                    over_limit = len(pending) >= MAX_SELECTED_CITIES and not already_selected
                    button_label = "已选" if already_selected else city
                    if st.button(button_label, key=f"add_browse_{city}", disabled=already_selected or over_limit, use_container_width=True):
                        sync_dashboard_cities(pending + [city], valid_cities)
                        st.rerun()

        action_cols = st.columns(2)
        with action_cols[0]:
            if st.button("清空选择", use_container_width=True):
                sync_dashboard_cities([], valid_cities)
                st.rerun()
        with action_cols[1]:
            if st.button("恢复默认", use_container_width=True):
                sync_dashboard_cities([city for city in DEFAULT_CITIES if city in valid_cities], valid_cities)
                st.rerun()

        if len(st.session_state["pending_selected_cities"]) > MAX_SELECTED_CITIES:
            st.warning(f"当前最多支持选择 {MAX_SELECTED_CITIES} 个城市，请减少选择数量。")


def normalize_forecast_time(value):
    fx_time = pd.to_datetime(value, errors="coerce")
    if pd.isna(fx_time):
        return None
    if getattr(fx_time, "tzinfo", None) is not None:
        fx_time = fx_time.tz_convert("Asia/Shanghai").tz_localize(None)
    return fx_time


def clamp_probability(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0
    return int(round(max(0, min(100, value))))


def precipitation_to_probability(value):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        amount = 0
    if amount <= 0:
        return 0
    if amount < 0.1:
        return 20
    if amount < 0.5:
        return 40
    if amount < 2:
        return 65
    if amount < 8:
        return 85
    return 95


OPEN_METEO_WEATHER_TEXT = {
    0: "晴",
    1: "少云",
    2: "多云",
    3: "阴",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "毛毛雨",
    55: "强毛毛雨",
    56: "冻毛毛雨",
    57: "强冻毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨",
    67: "强冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "阵雨",
    81: "强阵雨",
    82: "暴雨",
    85: "阵雪",
    86: "强阵雪",
    95: "雷阵雨",
    96: "雷阵雨伴小冰雹",
    99: "雷阵雨伴强冰雹",
}


@st.cache_data(ttl=WEATHER_CACHE_TTL_SECONDS, show_spinner=False)
def fetch_qweather_hourly(location_id, city_name, api_key, api_host):
    url = f"https://{api_host}/v7/weather/72h"
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip",
    }
    params = {
        "location": location_id,
        "lang": "zh",
        "unit": "m",
    }

    response = requests.get(url, headers=headers, params=params, timeout=12)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != "200":
        raise RuntimeError(f"接口返回 code={payload.get('code', 'unknown')}")

    rows = []
    for item in payload.get("hourly", []):
        fx_time = normalize_forecast_time(item.get("fxTime"))
        if fx_time is None:
            continue
        rows.append(
            {
                "city": city_name,
                "fxTime": fx_time,
                "date": fx_time.strftime("%Y-%m-%d"),
                "hour": fx_time.strftime("%H"),
                "text": item.get("text", ""),
                "source": "qweather",
                "source_weight": SOURCE_WEIGHTS["qweather"],
                "source_pop": clamp_probability(item.get("pop", 0)),
            }
        )
    return rows


@st.cache_data(ttl=WEATHER_CACHE_TTL_SECONDS, show_spinner=False)
def fetch_weatherapi_hourly(lon, lat, city_name, api_key):
    url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": f"{lat},{lon}",
        "days": 3,
        "aqi": "no",
        "alerts": "no",
        "lang": "zh",
    }
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        error = payload["error"]
        raise RuntimeError(error.get("message", "WeatherAPI 返回错误"))

    rows = []
    for day in payload.get("forecast", {}).get("forecastday", []):
        for item in day.get("hour", []):
            fx_time = normalize_forecast_time(item.get("time"))
            if fx_time is None:
                continue
            rows.append(
                {
                    "city": city_name,
                    "fxTime": fx_time,
                    "date": fx_time.strftime("%Y-%m-%d"),
                    "hour": fx_time.strftime("%H"),
                    "text": item.get("condition", {}).get("text", ""),
                    "source": "weatherapi",
                    "source_weight": SOURCE_WEIGHTS["weatherapi"],
                    "source_pop": clamp_probability(item.get("chance_of_rain", 0)),
                }
            )
    return rows


@st.cache_data(ttl=WEATHER_CACHE_TTL_SECONDS, show_spinner=False)
def fetch_open_meteo_hourly(lon, lat, city_name):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation_probability,weather_code",
        "forecast_hours": 72,
        "timezone": "Asia/Shanghai",
    }
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    payload = response.json()
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    probabilities = hourly.get("precipitation_probability", [])
    weather_codes = hourly.get("weather_code", [])

    rows = []
    for index, (fx_value, pop_value) in enumerate(zip(times, probabilities)):
        fx_time = normalize_forecast_time(fx_value)
        if fx_time is None:
            continue
        weather_code = weather_codes[index] if index < len(weather_codes) else None
        rows.append(
            {
                "city": city_name,
                "fxTime": fx_time,
                "date": fx_time.strftime("%Y-%m-%d"),
                "hour": fx_time.strftime("%H"),
                "text": OPEN_METEO_WEATHER_TEXT.get(weather_code, ""),
                "source": "open_meteo",
                "source_weight": SOURCE_WEIGHTS["open_meteo"],
                "source_pop": clamp_probability(pop_value),
            }
        )
    return rows


def blend_source_rows(source_rows, city_name):
    if not source_rows:
        return []

    source_df = pd.DataFrame(source_rows)
    blended_rows = []
    grouped = source_df.groupby(["city", "fxTime", "date", "hour"], as_index=False)
    for _, group in grouped:
        total_weight = group["source_weight"].sum()
        if total_weight <= 0:
            continue
        pop = int(round((group["source_pop"] * group["source_weight"]).sum() / total_weight))
        source_values = {
            f"{source}_pop": int(source_group["source_pop"].max())
            for source, source_group in group.groupby("source")
        }
        text_candidates = group[group["text"].fillna("").astype(str).str.strip() != ""].copy()
        if not text_candidates.empty:
            text_candidates = text_candidates.sort_values(["source_weight", "source_pop"], ascending=False)
            weather_text = str(text_candidates["text"].iloc[0]).strip()
        else:
            weather_text = "暂无"
        row = {
            "city": city_name,
            "fxTime": group["fxTime"].iloc[0],
            "date": group["date"].iloc[0],
            "hour": group["hour"].iloc[0],
            "text": weather_text,
            "pop": clamp_probability(pop),
            "source_count": int(group["source"].nunique()),
            "source_weight_total": int(total_weight),
        }
        row.update(source_values)
        blended_rows.append(row)
    return blended_rows


def fetch_selected_weather(city_df, selected_cities):
    if not selected_cities:
        st.warning("请至少选择一个城市。")
        return pd.DataFrame()

    if len(selected_cities) > MAX_SELECTED_CITIES:
        st.warning(f"当前最多支持选择 {MAX_SELECTED_CITIES} 个城市，请减少选择数量。")
        return pd.DataFrame()

    placeholder_values = {
        "请在这里填写我的和风天气API密钥",
        "请在这里填写我的和风天气专属API Host",
        "",
        None,
    }
    weatherapi_placeholder_values = {"请在这里填写我的WeatherAPI密钥", "", None}
    qweather_enabled = QWEATHER_API_KEY not in placeholder_values and QWEATHER_API_HOST not in placeholder_values
    weatherapi_enabled = WEATHERAPI_KEY not in weatherapi_placeholder_values
    if not qweather_enabled:
        st.warning("和风天气配置缺失，已跳过和风来源。")
    if not weatherapi_enabled:
        st.info("WeatherAPI Key 未配置，当前融合来源暂不包含 WeatherAPI。")

    city_info = city_df.set_index("city")[["location_id", "lat", "lon"]].to_dict("index")
    all_rows = []
    progress_text = st.empty()

    for city in selected_cities:
        info = city_info.get(city)
        if not info:
            st.warning(f"{city} 未在城市配置文件中找到 location_id，已跳过。")
            continue
        location_id = info["location_id"]
        lat = info["lat"]
        lon = info["lon"]
        source_rows = []

        if qweather_enabled:
            try:
                progress_text.caption(f"正在获取 {city} 的和风天气预报...")
                source_rows.extend(fetch_qweather_hourly(location_id, city, QWEATHER_API_KEY, QWEATHER_API_HOST))
            except Exception as exc:
                st.warning(f"{city} 和风天气请求失败：{exc}")

        if weatherapi_enabled:
            try:
                progress_text.caption(f"正在获取 {city} 的 WeatherAPI 预报...")
                source_rows.extend(fetch_weatherapi_hourly(lon, lat, city, WEATHERAPI_KEY))
            except Exception as exc:
                st.warning(f"{city} WeatherAPI 请求失败：{exc}")

        try:
            progress_text.caption(f"正在获取 {city} 的 Open-Meteo 预报...")
            source_rows.extend(fetch_open_meteo_hourly(lon, lat, city))
        except Exception as exc:
            st.warning(f"{city} Open-Meteo 请求失败：{exc}")

        all_rows.extend(blend_source_rows(source_rows, city))

    progress_text.empty()
    if not all_rows:
        st.error("没有获取到任何天气数据，请检查 API Key、API Host、网络或接口额度。")
        return pd.DataFrame()

    return pd.DataFrame(all_rows)


def build_date_options(weather_df):
    if weather_df.empty:
        today = pd.Timestamp.now().strftime("%Y-%m-%d")
        return [("今天", today), ("明天", ""), ("后天", "")]

    dates = sorted(weather_df["date"].dropna().unique().tolist())[:3]
    labels = ["今天", "明天", "后天"]
    return [(labels[index], date) for index, date in enumerate(dates)]


def make_heatmap_matrix(weather_df, selected_cities, selected_date):
    if weather_df.empty or not selected_date:
        return pd.DataFrame(index=selected_cities, columns=HOURS)

    day_df = weather_df[weather_df["date"] == selected_date]
    if day_df.empty:
        return pd.DataFrame(index=selected_cities, columns=HOURS)

    matrix = day_df.pivot_table(index="city", columns="hour", values="pop", aggfunc="max")
    matrix = matrix.reindex(index=selected_cities, columns=HOURS)
    return matrix


def build_weather_text_matrix(weather_df, selected_cities, selected_date):
    if weather_df.empty or not selected_date:
        return pd.DataFrame(index=selected_cities, columns=HOURS)

    day_df = weather_df[weather_df["date"] == selected_date]
    if day_df.empty or "text" not in day_df.columns:
        return pd.DataFrame(index=selected_cities, columns=HOURS)

    text_df = day_df.copy()
    text_df["text"] = text_df["text"].fillna("").astype(str)
    matrix = text_df.pivot_table(index="city", columns="hour", values="text", aggfunc="first")
    matrix = matrix.reindex(index=selected_cities, columns=HOURS)
    return matrix


def summarize_day_weather(weather_df, selected_cities, selected_date):
    summaries = {city: "暂无" for city in selected_cities}
    if weather_df.empty or not selected_date or "text" not in weather_df.columns:
        return summaries

    day_df = weather_df[weather_df["date"] == selected_date].copy()
    if day_df.empty:
        return summaries

    day_df["text"] = day_df["text"].fillna("").astype(str).str.strip()
    day_df = day_df[day_df["text"] != ""]
    if day_df.empty:
        return summaries

    for city in selected_cities:
        city_df = day_df[day_df["city"] == city]
        if city_df.empty:
            continue
        risky = city_df.sort_values("pop", ascending=False).head(6)
        counts = risky["text"].value_counts()
        if not counts.empty:
            summaries[city] = counts.index[0]
    return summaries


def rain_class(value):
    if pd.isna(value):
        return "rain-empty"
    if value < 30:
        return "rain-low"
    if value < 60:
        return "rain-mid"
    if value < 80:
        return "rain-high"
    return "rain-extreme"


def render_heatmap_html(matrix, text_matrix, day_weather):
    header_cells = "".join(f"<th>{hour}</th>" for hour in HOURS)
    rows = []
    for city, values in matrix.iterrows():
        city_weather = day_weather.get(city, "暂无")
        city_label = (
            f"<span class='city-name'>{html.escape(str(city))}</span>"
            f"<span class='city-weather'>｜{html.escape(str(city_weather))}</span>"
        )
        cells = [f"<td class='city-cell'>{city_label}</td>"]
        for hour in HOURS:
            value = values.get(hour)
            css_class = rain_class(value)
            label = "" if pd.isna(value) else f"{int(value)}%"
            weather_text = ""
            if text_matrix is not None and city in text_matrix.index and hour in text_matrix.columns:
                text_value = text_matrix.loc[city, hour]
                weather_text = "" if pd.isna(text_value) else str(text_value).strip()
            weather_text = weather_text or "暂无"
            tooltip = "\n".join(
                [
                    f"城市：{city}",
                    f"时段：{hour}:00",
                    f"天气：{weather_text}",
                    f"综合降雨概率：{label or '暂无'}",
                ]
            )
            escaped_tooltip = html.escape(tooltip, quote=True)
            cells.append(
                f"<td class='{css_class} rain-cell' data-tooltip='{escaped_tooltip}'>{label}</td>"
            )
        rows.append(f"<tr>{''.join(cells)}</tr>")

    heatmap_html = (
        '<div class="heatmap-wrap">'
        '<table class="rain-table">'
        f'<thead><tr><th class="city-head">城市</th>{header_cells}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</div>"
    )
    st.markdown(heatmap_html, unsafe_allow_html=True)


def build_summary(weather_df):
    if weather_df.empty:
        return {
            "max_pop": 0,
            "high_city_count": 0,
            "coverage": "等待数据",
            "source_count": 0,
        }

    max_pop = int(weather_df["pop"].max())
    high_city_count = int(weather_df.loc[weather_df["pop"] >= 60, "city"].nunique())
    start_time = weather_df["fxTime"].min().strftime("%m-%d %H:%M")
    end_time = weather_df["fxTime"].max().strftime("%m-%d %H:%M")
    source_count = int(weather_df.get("source_count", pd.Series([1])).max())
    return {
        "max_pop": max_pop,
        "high_city_count": high_city_count,
        "coverage": f"{start_time} - {end_time}",
        "source_count": source_count,
    }


def get_metrics(weather_df, selected_cities):
    summary = build_summary(weather_df)
    return [
        ("监测城市总数", f"{len(selected_cities)}", "当前已应用城市"),
        ("最高72小时降雨概率", f"{summary['max_pop']}%", "所选城市范围内"),
        ("≥60% 概率城市数", f"{summary['high_city_count']}", "未来72小时内"),
        ("数据覆盖时间", summary["coverage"], "来自逐小时预报"),
    ]


def render_metric_cards(weather_df, selected_cities):
    cols = st.columns(4)
    for col, (label, value, hint) in zip(cols, get_metrics(weather_df, selected_cities)):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{html.escape(label)}</div>
                    <div class="metric-value">{html.escape(value)}</div>
                    <div class="metric-hint">{html.escape(hint)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_status_chips(weather_df):
    summary = build_summary(weather_df)
    chips = [
        ("最高概率", f"{summary['max_pop']}%"),
        ("≥60%城市", f"{summary['high_city_count']}个"),
        ("融合来源", f"{summary['source_count']}个"),
    ]
    cols = st.columns(3)
    for col, (label, value) in zip(cols, chips):
        with col:
            st.markdown(
                f"""
                <div class="status-chip">
                    <div class="status-label">{html.escape(label)}</div>
                    <div class="status-value">{html.escape(value)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def get_day_risk_summary(weather_df, selected_date):
    if weather_df.empty or not selected_date:
        return {
            "top_city": "等待数据",
            "top_pop": "0%",
            "high_city_count": "0个",
            "risk_window": "等待数据",
        }

    day_df = weather_df[weather_df["date"] == selected_date].copy()
    if day_df.empty:
        return {
            "top_city": "暂无",
            "top_pop": "0%",
            "high_city_count": "0个",
            "risk_window": "暂无",
        }

    top_row = day_df.sort_values("pop", ascending=False).iloc[0]
    high_city_count = int(day_df.loc[day_df["pop"] >= 60, "city"].nunique())

    hourly_max = day_df.groupby("hour", as_index=False)["pop"].max().sort_values("pop", ascending=False)
    risk_hours = hourly_max.loc[hourly_max["pop"] >= 60, "hour"].head(4).tolist()
    if risk_hours:
        risk_window = "、".join(f"{hour}:00" for hour in sorted(risk_hours))
    else:
        risk_window = "暂无≥60%时段"

    return {
        "top_city": str(top_row["city"]),
        "top_pop": f"{int(top_row['pop'])}%",
        "high_city_count": f"{high_city_count}个",
        "risk_window": risk_window,
    }


def render_day_risk_summary(weather_df, selected_date):
    summary = get_day_risk_summary(weather_df, selected_date)
    value = f"{summary['top_city']} {summary['top_pop']}"
    st.markdown(
        f"""
        <div class="status-chip">
            <div class="status-label">最高风险城市</div>
            <div class="status-value">{html.escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top5(weather_df):
    if weather_df.empty:
        return "<div class='data-note'>等待天气数据。</div>"

    top5 = (
        weather_df.groupby("city", as_index=False)["pop"]
        .max()
        .sort_values("pop", ascending=False)
        .head(5)
    )
    pills = []
    for rank, (_, row) in enumerate(top5.iterrows(), start=1):
        pills.append(
            (
                '<div class="rank-pill">'
                f'<span class="rank-badge">{rank}</span>'
                f'<span class="rank-city">{html.escape(row["city"])}</span>'
                f'<strong class="rank-value">{int(row["pop"])}%</strong>'
                "</div>"
            )
        )
    return f"<div class='rank-pills'>{''.join(pills)}</div>"


def render_legend():
    legends = [
        ("rain-low", "0-29% 低概率"),
        ("rain-mid", "30-59% 中等概率"),
        ("rain-high", "60-79% 较高概率"),
        ("rain-extreme", "80%+ 高概率"),
    ]
    legend_html = "".join(
        (
            '<div class="legend-item">'
            f'<span class="legend-swatch {css_class}"></span>'
            f"<span>{html.escape(label)}</span>"
            "</div>"
        )
        for css_class, label in legends
    )
    return f"<div class='legend-grid'>{legend_html}</div>"


def render_data_note():
    return (
        '<div class="data-note">'
        "三源融合权重：Open-Meteo 4、和风天气 3、WeatherAPI 3。来源不可用时按实际可用来源计算；"
        "城市行展示当天代表性天气，悬停小时格查看详情。缓存 3 小时。"
        "</div>"
    )


def render_support_strip(weather_df):
    st.markdown(
        (
            '<div class="support-strip">'
            '<div class="support-item">'
            '<div class="module-title">72小时最高降雨概率 TOP5</div>'
            f"{render_top5(weather_df)}"
            "</div>"
            '<div class="support-item">'
            '<div class="module-title">降雨概率图例</div>'
            f"{render_legend()}"
            "</div>"
            '<div class="support-item">'
            '<div class="module-title">数据说明</div>'
            f"{render_data_note()}"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_header():
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(
        f"""
        <div class="dashboard-header">
            <div>
                <div class="dashboard-title">城市72小时降雨概率雷达</div>
                <div class="dashboard-subtitle">更新时间：{html.escape(updated_at)}</div>
            </div>
            <div class="service-label">气象数据服务中心</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    page_config()
    inject_styles()
    render_header()

    city_df = load_city_locations()
    if city_df is None:
        st.error("未找到城市配置文件 data/china_city_locations.csv，请先补充城市数据。")
        return

    try:
        init_session_state(city_df)
    except Exception as exc:
        st.error(f"初始化城市数据失败：{exc}")
        return

    selected_cities = clean_selected_cities(
        st.session_state.get("selected_cities", []),
        city_df["city"].tolist(),
    )
    st.session_state["selected_cities"] = selected_cities

    weather_df = fetch_selected_weather(city_df, selected_cities)

    date_options = build_date_options(weather_df)
    option_labels = [f"{label} {date}" if date else label for label, date in date_options]
    default_label = option_labels[0] if option_labels else ""
    current_label = st.session_state.get("selected_date_label", default_label)
    if current_label not in option_labels:
        current_label = default_label
    selected_date = dict(zip(option_labels, [date for _, date in date_options])).get(current_label, "")

    op_cols = st.columns([1.55, 1.35, 1.25])
    with op_cols[0]:
        with st.container(border=True):
            st.markdown("<div class='operation-caption'>城市筛选</div>", unsafe_allow_html=True)
            st.markdown("<div class='operation-title'>当前监测城市</div>", unsafe_allow_html=True)
            render_city_selector(city_df)
    with op_cols[1]:
        with st.container(border=True):
            st.markdown("<div class='operation-caption'>天维度筛选</div>", unsafe_allow_html=True)
            st.markdown("<div class='operation-title'>选择查看日期</div>", unsafe_allow_html=True)
            selected_label = st.radio(
                "日期切换",
                option_labels,
                horizontal=True,
                label_visibility="collapsed",
                key="selected_date_label",
            )
    with op_cols[2]:
        with st.container(border=True):
            st.markdown("<div class='operation-caption'>当前日期风险</div>", unsafe_allow_html=True)
            st.markdown("<div class='operation-title'>最高风险城市</div>", unsafe_allow_html=True)
            render_day_risk_summary(weather_df, selected_date)

    selected_date = dict(zip(option_labels, [date for _, date in date_options])).get(selected_label, "")
    matrix = make_heatmap_matrix(weather_df, selected_cities, selected_date)
    text_matrix = build_weather_text_matrix(weather_df, selected_cities, selected_date)
    day_weather = summarize_day_weather(weather_df, selected_cities, selected_date)

    with st.container(border=True):
        context = (
            f"当前查看：{selected_label}｜共 {len(selected_cities)} 城市"
            if selected_label
            else f"共 {len(selected_cities)} 城市"
        )
        st.markdown(
            f"""
            <div class="heatmap-topline">
                <div>
                    <div class="operation-caption">核心看板</div>
                    <div class="heatmap-title">分小时综合降雨概率（%）</div>
                </div>
                <div class="heatmap-context">{html.escape(context)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_heatmap_html(matrix, text_matrix, day_weather)

    render_support_strip(weather_df)


if __name__ == "__main__":
    main()
