import html
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
CITY_FILE = BASE_DIR / "data" / "china_city_pool.csv"
LEGACY_CITY_FILE = BASE_DIR / "data" / "china_city_locations.csv"
HOURS = [f"{hour:02d}" for hour in range(24)]
TIMEZONE = ZoneInfo("Asia/Shanghai")


def build_date_options():
    today = datetime.now(TIMEZONE).date()
    labels = ["今天", "明天", "后天"]
    return [
        (label, (today + timedelta(days=offset)).strftime("%m-%d"), (today + timedelta(days=offset)).isoformat())
        for offset, label in enumerate(labels)
    ]


def current_update_time():
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M")


DATE_OPTIONS = build_date_options()
RISK_OPTIONS = ["全部风险", "高风险", "中高风险", "中低风险", "低风险"]
MAX_DISPLAY_CITIES = 15

CITY_PROVINCES = {
    "上海市": "上海",
    "深圳市": "广东",
    "大连市": "辽宁",
    "天津市": "天津",
    "西安市": "陕西",
    "无锡市": "江苏",
    "长沙市": "湖南",
    "杭州市": "浙江",
    "成都市": "四川",
    "宁波市": "浙江",
    "苏州市": "江苏",
    "南京市": "江苏",
    "青岛市": "山东",
    "沈阳市": "辽宁",
    "济南市": "山东",
}
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
KEYWORD_PACKAGES = ["长三角", "珠三角", "华东", "华南", "西南", "重点经营", "高收入", "雨天敏感", "场站城市", "暑期旅游"]

# Mock data mirrors the provided reference so the page can run without API calls.
MOCK_ROWS = [
    ("上海市", "阵雨", 90, "09-11时", [60, 50, 46, 47, 53, 50, 45, 65, 77, 90, 87, 76, 78, 82, 75, 56, 69, 68, 67, 51, 52, 70, 70, 69]),
    ("深圳市", "雷阵雨", 34, "12-14时", [17, 29, 29, 28, 28, 29, 29, 18, 13, 8, 10, 14, 18, 34, 37, 32, 18, 14, 11, 8, 4, 4, 4, 4]),
    ("大连市", "晴天", 8, "00-03时", [5, 6, 8, 8, 8, 8, 8, 7, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4]),
    ("天津市", "多云", 24, "17-19时", [3, 1, 1, 2, 2, 2, 2, 2, 1, 0, 1, 1, 1, 2, 21, 3, 4, 24, 4, 8, 23, 6, 12, 17]),
    ("西安市", "阴", 31, "20-22时", [10, 10, 10, 10, 10, 10, 12, 10, 8, 3, 4, 4, 6, 9, 11, 12, 13, 17, 12, 12, 11, 31, 29, 29]),
    ("无锡市", "阵雨", 67, "08-12时", [30, 31, 30, 30, 34, 42, 33, 31, 31, 60, 57, 60, 63, 64, 65, 64, 64, 64, 66, 67, 66, 63, 60, 58]),
    ("长沙市", "小阵雨", 77, "00-03时", [46, 58, 62, 59, 74, 53, 77, 73, 64, 74, 67, 77, 70, 70, 64, 62, 59, 56, 56, 56, 55, 38, 37, 34]),
    ("杭州市", "小阵雨", 86, "05-11时", [48, 71, 77, 62, 55, 71, 86, 85, 81, 82, 82, 81, 80, 70, 72, 78, 77, 75, 80, 73, 78, 77, 72, 73]),
    ("成都市", "小毛毛雨", 50, "14-16时", [31, 27, 30, 17, 19, 26, 23, 25, 23, 8, 6, 24, 12, 40, 47, 50, 27, 23, 38, 34, 29, 10, 7, 10]),
    ("宁波市", "小阵雨", 84, "00-07时", [76, 54, 84, 83, 80, 81, 81, 72, 69, 66, 54, 63, 63, 63, 70, 76, 78, 78, 76, 65, 70, 72, 74, 62]),
    ("苏州市", "阵雨", 78, "10-15时", [31, 31, 33, 37, 44, 64, 63, 46, 50, 71, 72, 78, 74, 69, 70, 69, 69, 68, 68, 48, 48, 66, 66, 65]),
    ("南京市", "小毛毛雨", 53, "20-22时", [32, 37, 42, 33, 40, 44, 35, 30, 27, 53, 40, 58, 59, 42, 62, 57, 40, 36, 33, 29, 44, 42, 40, 38]),
    ("青岛市", "晴天", 20, "20-22时", [12, 13, 13, 13, 14, 13, 11, 1, 2, 3, 3, 2, 2, 3, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]),
    ("沈阳市", "阴", 59, "20-22时", [3, 3, 4, 4, 6, 3, 3, 3, 3, 3, 4, 4, 4, 8, 8, 13, 14, 12, 12, 44, 42, 49, 59, 46]),
    ("济南市", "晴天", 6, "00-03时", [3, 3, 5, 6, 7, 7, 7, 7, 6, 0, 0, 1, 1, 2, 3, 4, 3, 3, 2, 0, 0, 1, 2, 3]),
]


def page_config():
    st.set_page_config(
        page_title="城市72小时降雨概率雷达",
        page_icon="☔",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --blue: #1677ff;
            --blue-dark: #0d3470;
            --text: #14345f;
            --muted: #5e7395;
            --line: #dbe8f6;
            --panel: rgba(255, 255, 255, 0.92);
            --green-bg: #e7f7eb;
            --green-text: #0b6b46;
            --yellow-bg: #fff3c8;
            --yellow-text: #79560c;
            --orange-bg: #ffd9b7;
            --orange-text: #9a4b00;
            --red-bg: #ffd1d7;
            --red-text: #c5112f;
        }

        .stApp {
            background:
                radial-gradient(circle at 18% 0%, rgba(255,255,255,0.95), rgba(255,255,255,0) 24%),
                linear-gradient(180deg, #edf7ff 0%, #f7fbff 42%, #ffffff 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1880px;
            padding: 18px 26px 104px;
        }

        header[data-testid="stHeader"],
        #MainMenu,
        footer,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stDeployButton"],
        [data-testid="stStatusWidget"],
        [data-testid="stConnectionStatus"],
        [data-testid="manage-app-button"],
        .stStatusWidget,
        .stDeployButton {
            display: none !important;
            visibility: hidden !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.75rem;
        }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 10px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
            min-width: 0;
        }

        .brand-icon {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            background: #e9f4ff;
            color: var(--blue);
            font-size: 25px;
            box-shadow: inset 0 0 0 1px rgba(22,119,255,0.14);
        }

        .brand-title {
            font-size: 28px;
            line-height: 1.1;
            color: #0f3267;
            font-weight: 850;
            letter-spacing: 0;
        }

        .brand-sub {
            display: inline-flex;
            align-items: center;
            height: 22px;
            margin-top: 6px;
            padding: 0 9px;
            border-radius: 999px;
            background: #eaf4ff;
            color: #2b6db8;
            font-size: 12px;
            font-weight: 800;
        }

        .service {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #385883;
            font-weight: 800;
            white-space: nowrap;
        }

        .refresh-btn {
            border: none;
            background: #1677ff;
            color: white;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 13px;
            font-weight: 850;
            box-shadow: 0 8px 18px rgba(22,119,255,0.20);
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 12px;
        }

        .summary-card {
            min-height: 108px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            box-shadow: 0 12px 28px rgba(29, 89, 143, 0.08);
            padding: 18px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .summary-icon {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background: #f1f7ff;
            color: var(--blue);
            font-size: 24px;
            flex: 0 0 auto;
        }

        .summary-label {
            color: #244b7d;
            font-size: 14px;
            font-weight: 850;
            margin-bottom: 8px;
        }

        .summary-value {
            color: #0f3c78;
            font-size: 25px;
            font-weight: 900;
            line-height: 1.1;
        }

        .summary-value.danger {
            color: #f00636;
        }

        .summary-hint {
            margin-top: 8px;
            color: #6680a3;
            font-size: 12px;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .filterbar {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,0.95);
            box-shadow: 0 10px 22px rgba(29, 89, 143, 0.06);
            padding: 10px 14px;
            margin-bottom: 12px;
            display: grid;
            grid-template-columns: minmax(250px, 0.8fr) minmax(300px, 1.05fr) minmax(220px, 0.8fr) minmax(260px, 0.75fr);
            gap: 14px;
            align-items: center;
        }

        .filter-group {
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
        }

        .filter-label {
            color: #254c7d;
            font-size: 13px;
            font-weight: 850;
            margin-bottom: 7px;
            white-space: nowrap;
        }

        .city-count {
            color: #1d5fae;
            font-weight: 900;
        }

        .city-filter-card {
            min-height: 74px;
        }

        .city-filter-card .stButton {
            margin-top: 8px;
        }

        .segmented,
        .toolbar-actions {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .chip {
            border: 1px solid #cdddf0;
            background: #f8fbff;
            color: #244b7d;
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: 800;
            line-height: 1;
        }

        .chip.active {
            border-color: rgba(22,119,255,0.32);
            background: #e8f2ff;
            color: var(--blue);
        }

        .chip.primary {
            border-color: var(--blue);
            background: var(--blue);
            color: white;
        }

        .table-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,0.96);
            box-shadow: 0 14px 32px rgba(29, 89, 143, 0.08);
            padding: 14px;
        }

        .table-heading {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }

        .table-title {
            color: #0f3267;
            font-size: 21px;
            font-weight: 900;
        }

        .table-note {
            color: #627a9e;
            font-size: 12px;
            font-weight: 750;
        }

        .table-wrap {
            overflow-x: auto;
            border: 1px solid #dce8f5;
            border-radius: 6px;
            background: white;
            max-width: 100%;
            -webkit-overflow-scrolling: touch;
            overscroll-behavior-x: contain;
        }

        .rain-table {
            width: 100%;
            min-width: 1560px;
            border-collapse: separate;
            border-spacing: 0;
            table-layout: fixed;
            font-size: 13px;
        }

        .rain-table th {
            height: 36px;
            background: #f3f8fe;
            color: #143d72;
            border-bottom: 1px solid #dce8f5;
            border-right: 1px solid #e6eef8;
            font-weight: 900;
            white-space: nowrap;
        }

        .rain-table td {
            height: 31px;
            text-align: center;
            border-bottom: 1px solid #edf2f8;
            border-right: 1px solid #edf2f8;
            font-weight: 850;
            white-space: nowrap;
        }

        .rain-table tr:last-child td {
            border-bottom: none;
        }

        .col-city { width: 84px; }
        .col-weather { width: 92px; }
        .col-max { width: 86px; }
        .col-window { width: 102px; }
        .col-hour { width: 46px; }

        .city-cell {
            color: #10386f;
            text-align: left !important;
            padding-left: 12px;
            background: #fbfdff;
        }

        .weather-cell,
        .window-cell {
            color: #385d8c;
            background: #fbfdff;
        }

        .rain-table .col-city,
        .rain-table .city-cell {
            position: sticky;
            left: 0;
            z-index: 4;
        }

        .rain-table .col-weather,
        .rain-table .weather-cell {
            position: sticky;
            left: 84px;
            z-index: 4;
        }

        .rain-table .col-max,
        .rain-table td:nth-child(3) {
            position: sticky;
            left: 176px;
            z-index: 4;
            background-clip: padding-box;
        }

        .rain-table .col-window,
        .rain-table .window-cell {
            position: sticky;
            left: 262px;
            z-index: 4;
        }

        .rain-table th.col-city,
        .rain-table th.col-weather,
        .rain-table th.col-max,
        .rain-table th.col-window {
            z-index: 5;
        }

        .max-low { color: var(--green-text); }
        .max-mid { color: var(--yellow-text); }
        .max-high { color: var(--orange-text); }
        .max-extreme { color: #f00636; }

        .risk-low {
            background: var(--green-bg);
            color: var(--green-text);
        }

        .risk-mid {
            background: var(--yellow-bg);
            color: var(--yellow-text);
        }

        .risk-high {
            background: var(--orange-bg);
            color: var(--orange-text);
        }

        .risk-extreme {
            background: var(--red-bg);
            color: var(--red-text);
        }

        .bottom-panel {
            display: grid;
            grid-template-columns: 1.05fr 0.85fr 1.3fr;
            gap: 20px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,0.94);
            box-shadow: 0 10px 24px rgba(29, 89, 143, 0.06);
            padding: 18px 20px;
            margin-top: 12px;
        }

        .bottom-section {
            min-width: 0;
            border-right: 1px solid #dce8f5;
            padding-right: 20px;
        }

        .bottom-section:last-child {
            border-right: none;
            padding-right: 0;
        }

        .bottom-title {
            color: #0f3267;
            font-size: 16px;
            font-weight: 900;
            margin-bottom: 12px;
        }

        .top5-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
        }

        .rank-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            min-height: 30px;
            border-radius: 999px;
            border: 1px solid #f3d7d7;
            background: #fffafa;
            padding: 4px 10px 4px 5px;
            color: #153a70;
            font-size: 13px;
            font-weight: 900;
        }

        .rank-no {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: inline-grid;
            place-items: center;
            background: #ff6d7d;
            color: #fff;
            font-size: 12px;
            flex: 0 0 auto;
        }

        .rank-value {
            color: #f00636;
            margin-left: auto;
        }

        .legend-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px 22px;
        }

        .heatmap-legend {
            align-items: center;
            min-width: min(520px, 100%);
            margin-left: auto;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #385d8c;
            font-size: 13px;
            font-weight: 800;
        }

        .swatch {
            width: 34px;
            height: 16px;
            border-radius: 5px;
            border: 1px solid rgba(0,0,0,0.04);
        }

        .data-copy {
            color: #4f6990;
            font-size: 13px;
            line-height: 1.8;
            font-weight: 700;
        }

        .stButton > button {
            border-radius: 7px;
            border: 1px solid #cdddf0;
            color: #244b7d;
            background: #f8fbff;
            font-weight: 850;
        }

        .stButton > button[kind="primary"] {
            background: var(--blue);
            border-color: var(--blue);
            color: #fff;
        }

        div[data-testid="stDialog"] div[role="dialog"] {
            border-radius: 10px;
            max-width: 1040px;
            max-height: 88vh;
            overflow-y: auto;
            width: 94vw;
        }

        div[data-testid="stDialog"] div[data-testid="stVerticalBlock"] {
            gap: 0.55rem;
        }

        .city-entry {
            border: 1px solid #e1ebf7;
            background: #fbfdff;
            border-radius: 8px;
            padding: 8px 10px;
            min-height: 52px;
            margin-bottom: 8px;
        }

        .city-entry-name {
            color: #14345f;
            font-size: 14px;
            font-weight: 900;
            line-height: 1.3;
        }

        .city-entry-meta {
            color: #6c82a1;
            font-size: 12px;
            font-weight: 700;
            margin-top: 3px;
        }

        .city-manager-note {
            color: #5a7398;
            font-size: 12px;
            line-height: 1.55;
            font-weight: 700;
        }

        .selected-city-row {
            border: 1px solid #dbe8f6;
            background: #ffffff;
            border-radius: 8px;
            padding: 8px;
            margin-bottom: 8px;
        }

        @media (max-width: 1200px) {
            .summary-grid,
            .filterbar,
            .bottom-panel {
                grid-template-columns: 1fr;
            }

            .bottom-section {
                border-right: none;
                border-bottom: 1px solid #dce8f5;
                padding-right: 0;
                padding-bottom: 14px;
            }
        }

        @media (max-width: 700px) {
            .block-container {
                padding: 12px 10px calc(128px + env(safe-area-inset-bottom));
            }

            .topbar {
                gap: 8px;
            }

            .brand {
                gap: 10px;
            }

            .brand-icon {
                width: 38px;
                height: 38px;
                border-radius: 10px;
                font-size: 21px;
            }

            .brand-title {
                font-size: 21px;
            }

            .service {
                flex-wrap: wrap;
                gap: 6px 10px;
                white-space: normal;
                font-size: 12px;
            }

            .summary-card {
                min-height: auto;
                padding: 12px;
                gap: 12px;
            }

            .summary-icon {
                width: 42px;
                height: 42px;
                font-size: 20px;
            }

            .summary-label {
                font-size: 13px;
                margin-bottom: 5px;
            }

            .summary-value {
                font-size: 20px;
            }

            .filter-label,
            .city-preview {
                white-space: normal;
            }

            .table-card {
                padding: 10px 8px;
            }

            .table-heading {
                align-items: flex-start;
            }

            .table-title {
                font-size: 17px;
            }

            .heatmap-legend {
                width: 100%;
                margin-left: 0;
                grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
                gap: 8px 10px;
            }

            .legend-item {
                gap: 7px;
                font-size: 12px;
            }

            .swatch {
                width: 28px;
                height: 14px;
                flex: 0 0 auto;
            }

            .rain-table {
                min-width: 1120px;
                font-size: 12px;
            }

            .rain-table th {
                height: 32px;
            }

            .rain-table td {
                height: 30px;
            }

            .col-city { width: 72px; }
            .col-weather { width: 82px; }
            .col-max { width: 76px; }
            .col-window { width: 86px; }
            .col-hour { width: 36px; }

            .rain-table .col-weather,
            .rain-table .weather-cell,
            .rain-table .col-max,
            .rain-table td:nth-child(3),
            .rain-table .col-window,
            .rain-table .window-cell {
                position: static;
                left: auto;
            }

            .rain-table .col-city,
            .rain-table .city-cell {
                position: sticky;
                left: 0;
                z-index: 4;
            }

            .rain-table th.col-city {
                z-index: 5;
            }

            .city-cell {
                padding-left: 8px;
            }

            .bottom-panel {
                gap: 12px;
                margin-top: 10px;
                padding: 14px 12px;
            }

            .top5-grid,
            .legend-grid {
                grid-template-columns: 1fr;
            }

            div[data-testid="stDialog"] div[role="dialog"] {
                width: 96vw;
                max-height: 86vh;
            }

            .city-entry {
                min-height: 44px;
                padding: 6px 8px;
                margin-bottom: 6px;
            }

            .selected-city-row {
                padding: 6px;
                margin-bottom: 6px;
            }

            .city-entry-name {
                font-size: 13px;
            }

            .city-entry-meta,
            .city-manager-note {
                font-size: 11px;
            }

            .stButton > button {
                min-height: 34px;
                padding: 0.35rem 0.45rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_base_dataframe():
    """Build the 15-city hourly probability table used by all views."""
    rows = []
    for city, weather, max_prob, risk_window, values in MOCK_ROWS:
        row = {
            "city": city,
            "province": CITY_PROVINCES.get(city, ""),
            "weather": weather,
            "max_prob": max_prob,
            "risk_window": risk_window,
        }
        row.update({hour: values[index] for index, hour in enumerate(HOURS)})
        rows.append(row)
    return pd.DataFrame(rows)


@st.cache_data
def load_city_catalog():
    source_file = CITY_FILE if CITY_FILE.exists() else LEGACY_CITY_FILE
    if not source_file.exists():
        return pd.DataFrame(
            [
                {
                    "province": province,
                    "city": city,
                    "city_code": "",
                    "location_id": "",
                    "lat": 0.0,
                    "lon": 0.0,
                    "region": "",
                    "city_level": "地级市",
                    "tags": "",
                }
                for city, province in CITY_PROVINCES.items()
            ]
        )
    catalog = pd.read_csv(source_file, dtype={"location_id": str})
    defaults = {
        "province": "",
        "city": "",
        "city_code": "",
        "location_id": "",
        "lat": 0.0,
        "lon": 0.0,
        "region": "",
        "city_level": "地级市",
        "tags": "",
    }
    for column, default in defaults.items():
        if column not in catalog.columns:
            catalog[column] = default
    catalog["city"] = catalog["city"].astype(str).str.strip()
    catalog["province"] = catalog["province"].astype(str).str.strip()
    catalog["region"] = catalog["region"].astype(str).str.strip()
    catalog["tags"] = catalog["tags"].fillna("").astype(str).replace("nan", "")
    return catalog[list(defaults.keys())].drop_duplicates(subset=["city"]).reset_index(drop=True)


def city_province_map():
    catalog = load_city_catalog()
    return catalog.set_index("city")["province"].to_dict()


def generated_city_row(city, province):
    seed = sum(ord(char) for char in city)
    weather_options = ["晴天", "多云", "阴", "小阵雨", "阵雨", "小毛毛雨", "雷阵雨"]
    weather = weather_options[seed % len(weather_options)]
    peak_start = seed % 21
    base = seed % 24
    values = []
    for hour in range(24):
        distance = min(abs(hour - peak_start), abs(hour - peak_start - 24), abs(hour - peak_start + 24))
        wave = max(0, 42 - distance * 7)
        value = max(0, min(95, base + wave + ((seed + hour * 11) % 13) - 6))
        values.append(int(value))

    max_prob = max(values)
    risk_window = f"{peak_start:02d}-{min(23, peak_start + 2):02d}时"
    row = {
        "city": city,
        "province": province,
        "weather": weather,
        "max_prob": max_prob,
        "risk_window": risk_window,
    }
    row.update({hour: values[index] for index, hour in enumerate(HOURS)})
    return row


def build_dataframe_for_cities(cities):
    base = build_base_dataframe().set_index("city", drop=False)
    provinces = city_province_map()
    rows = []
    for city in cities:
        if city in base.index:
            row = base.loc[city].to_dict()
            row["province"] = provinces.get(city, row.get("province", ""))
            rows.append(row)
        elif city in provinces:
            rows.append(generated_city_row(city, provinces[city]))
    return pd.DataFrame(rows)


def shifted_dataframe(date_key, cities=None):
    """Create lightweight mock variants for today, tomorrow, and the day after."""
    base = build_dataframe_for_cities(cities or DEFAULT_CITIES)
    date_keys = [option[2] for option in DATE_OPTIONS]
    offset_values = [0, -7, 5]
    offsets = dict(zip(date_keys, offset_values))
    offset = offsets.get(date_key, 0)
    if offset == 0:
        return base

    adjusted = base.copy()
    for hour in HOURS:
        adjusted[hour] = adjusted[hour].apply(lambda value: max(0, min(100, int(value + offset))))
    adjusted["max_prob"] = adjusted[HOURS].max(axis=1)
    return adjusted


def risk_class(value):
    if value >= 80:
        return "risk-extreme"
    if value >= 60:
        return "risk-high"
    if value >= 30:
        return "risk-mid"
    return "risk-low"


def max_class(value):
    if value >= 80:
        return "max-extreme"
    if value >= 60:
        return "max-high"
    if value >= 30:
        return "max-mid"
    return "max-low"


def weather_icon(weather):
    if "雷" in weather:
        return "⛈"
    if "雨" in weather or "毛毛" in weather:
        return "☔"
    if "晴" in weather:
        return "☀"
    return "☁"


def risk_legend_html():
    items = [
        ("risk-low", "0-29%　低概率"),
        ("risk-mid", "30-59%　中等概率"),
        ("risk-high", "60-79%　较高概率"),
        ("risk-extreme", "≥80%　高风险"),
    ]
    return "".join(
        (
            '<div class="legend-item">'
            f'<span class="swatch {css_class}"></span>'
            f"<span>{html.escape(label)}</span>"
            "</div>"
        )
        for css_class, label in items
    )


def apply_risk_filter(df, risk_filter):
    if risk_filter == "高风险":
        return df[df["max_prob"] >= 80]
    if risk_filter == "中高风险":
        return df[(df["max_prob"] >= 60) & (df["max_prob"] <= 79)]
    if risk_filter == "中低风险":
        return df[(df["max_prob"] >= 30) & (df["max_prob"] <= 59)]
    if risk_filter == "低风险":
        return df[df["max_prob"] <= 29]
    return df


def initialize_state():
    st.session_state.setdefault("selected_cities", list(DEFAULT_CITIES))
    st.session_state.setdefault("pending_selected_cities", list(st.session_state["selected_cities"]))
    st.session_state.setdefault("replace_city_index", None)
    st.session_state.setdefault("city_groups", {"默认15城": list(DEFAULT_CITIES)})
    st.session_state.setdefault("default_city_group", "默认15城")
    st.session_state.setdefault("selected_date", DATE_OPTIONS[0][2])
    st.session_state.setdefault("risk_filter", RISK_OPTIONS[0])
    st.session_state.setdefault("show_city_selector", False)


def valid_city_set():
    catalog = load_city_catalog()
    usable = catalog[catalog["location_id"].fillna("").astype(str).str.strip() != ""]
    return set(usable["city"].tolist())


def clean_city_list(cities):
    valid = valid_city_set()
    cleaned = []
    for city in cities:
        if city in valid and city not in cleaned:
            cleaned.append(city)
    return cleaned


def open_city_manager():
    st.session_state["pending_selected_cities"] = clean_city_list(st.session_state["selected_cities"])
    st.session_state["replace_city_index"] = None
    st.session_state["show_city_selector"] = True


def pending_cities():
    return clean_city_list(st.session_state.get("pending_selected_cities", []))


def set_pending(cities):
    st.session_state["pending_selected_cities"] = clean_city_list(cities)


def add_pending_city(city):
    pending = pending_cities()
    replace_index = st.session_state.get("replace_city_index")
    if replace_index is not None and 0 <= replace_index < len(pending):
        if city in pending and pending[replace_index] != city:
            st.session_state["city_manager_message"] = "该城市已在当前列表中，不能重复选择。"
            return
        pending[replace_index] = city
        st.session_state["replace_city_index"] = None
        set_pending(pending)
        return
    if city in pending:
        st.session_state["city_manager_message"] = "该城市已在当前列表中。"
        return
    if len(pending) >= MAX_DISPLAY_CITIES:
        st.session_state["city_manager_message"] = "当前看板最多展示15个城市，请先移除一个城市后再添加。"
        return
    set_pending(pending + [city])


def remove_pending_city(city):
    pending = [item for item in pending_cities() if item != city]
    set_pending(pending)


def move_pending_city(index, direction):
    pending = pending_cities()
    target = index + direction
    if 0 <= index < len(pending) and 0 <= target < len(pending):
        pending[index], pending[target] = pending[target], pending[index]
        set_pending(pending)


def replace_pending_city(index):
    st.session_state["replace_city_index"] = index
    pending = pending_cities()
    if 0 <= index < len(pending):
        st.session_state["city_manager_message"] = f"正在替换 {pending[index]}，请在搜索结果中选择新城市。"


def clear_pending_cities():
    set_pending([])


def restore_default_pending():
    default_group = st.session_state.get("default_city_group", "默认15城")
    cities = st.session_state.get("city_groups", {}).get(default_group, DEFAULT_CITIES)
    set_pending(cities[:MAX_DISPLAY_CITIES])


def apply_keyword_matches(cities, mode):
    matches = clean_city_list(cities)
    if len(matches) > MAX_DISPLAY_CITIES:
        st.session_state["city_manager_message"] = "匹配城市超过15个，已默认取前15个。"
        matches = matches[:MAX_DISPLAY_CITIES]
    if mode == "replace":
        set_pending(matches)
    elif mode == "add":
        pending = pending_cities()
        for city in matches:
            if city not in pending:
                if len(pending) >= MAX_DISPLAY_CITIES:
                    st.session_state["city_manager_message"] = "当前看板最多展示15个城市，请先移除一个城市后再添加。"
                    break
                pending.append(city)
        set_pending(pending)


def rerun_app():
    try:
        st.rerun(scope="app")
    except TypeError:
        st.rerun()


def confirm_city_selection():
    pending = pending_cities()
    if not pending:
        st.warning("请至少选择一个城市。")
        return
    if len(pending) > MAX_DISPLAY_CITIES:
        st.warning(f"最多选择 {MAX_DISPLAY_CITIES} 个城市，请先移除部分城市。")
        return
    st.session_state["selected_cities"] = list(pending)
    st.session_state["replace_city_index"] = None
    st.session_state["show_city_selector"] = False
    rerun_app()


def cancel_city_selection():
    st.session_state["pending_selected_cities"] = list(st.session_state["selected_cities"])
    st.session_state["replace_city_index"] = None
    st.session_state["show_city_selector"] = False
    rerun_app()


def save_city_group(name):
    clean_name = str(name).strip()
    if not clean_name:
        st.session_state["city_manager_message"] = "请输入城市组合名称。"
        return
    pending = pending_cities()
    if not pending:
        st.session_state["city_manager_message"] = "请至少选择一个城市后再保存组合。"
        return
    st.session_state["city_groups"][clean_name] = pending


def apply_city_group(name):
    group = st.session_state.get("city_groups", {}).get(name)
    if group:
        set_pending(group[:MAX_DISPLAY_CITIES])


def rename_city_group(old_name, new_name):
    clean_name = str(new_name).strip()
    groups = st.session_state.get("city_groups", {})
    if not old_name or old_name not in groups or not clean_name:
        return
    groups[clean_name] = groups.pop(old_name)
    if st.session_state.get("default_city_group") == old_name:
        st.session_state["default_city_group"] = clean_name


def delete_city_group(name):
    if name == "默认15城":
        st.session_state["city_manager_message"] = "默认15城不能删除。"
        return
    groups = st.session_state.get("city_groups", {})
    groups.pop(name, None)
    if st.session_state.get("default_city_group") == name:
        st.session_state["default_city_group"] = "默认15城"


def set_default_city_group(name):
    if name in st.session_state.get("city_groups", {}):
        st.session_state["default_city_group"] = name


def render_header():
    updated_at = current_update_time()
    header_html = (
        '<div class="topbar">'
        '<div class="brand">'
        '<div class="brand-icon">☔</div>'
        '<div>'
        '<div class="brand-title">城市72小时降雨概率雷达</div>'
        '<div class="brand-sub">72小时监测</div>'
        "</div>"
        "</div>"
        '<div class="service">'
        "<span>气象数据服务中心</span>"
        f"<span>更新时间：{html.escape(updated_at)}</span>"
        '<button class="refresh-btn">刷新数据</button>'
        "</div>"
        "</div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)


def render_summary_cards(df):
    if df.empty:
        st.info("当前没有可展示城市，请在城市管理中至少选择一个城市。")
        return

    updated_at = current_update_time()
    high_df = df[df["max_prob"] >= 80].sort_values("max_prob", ascending=False)
    top = df.sort_values("max_prob", ascending=False).iloc[0]
    high_names = "、".join(high_df["city"].tolist()) or "暂无"

    cards = [
        ("🛡", "最高风险城市", f"{top['city']}　{int(top['max_prob'])}%", f"最高时段：{top['risk_window']}", "danger"),
        ("🛡", "高风险城市数", f"{len(high_df)} 个", high_names, ""),
        ("◷", "风险高峰时段", "09:00 - 11:00", "未来72小时内风险最集中的时段", ""),
        ("▧", "数据更新时间 / 数据源", updated_at, "数据源：本地 Mock，可无 API Key 运行", ""),
    ]
    card_html = "".join(
        (
            '<div class="summary-card">'
            f'<div class="summary-icon">{icon}</div>'
            "<div>"
            f'<div class="summary-label">{html.escape(label)}</div>'
            f'<div class="summary-value {value_class}">{html.escape(value)}</div>'
            f'<div class="summary-hint">{html.escape(hint)}</div>'
            "</div>"
            "</div>"
        )
        for icon, label, value, hint, value_class in cards
    )
    st.markdown(f"<div class='summary-grid'>{card_html}</div>", unsafe_allow_html=True)


def set_date(date_key):
    st.session_state["selected_date"] = date_key


def set_risk_filter(option):
    st.session_state["risk_filter"] = option


def render_filter_bar():
    with st.container(border=True):
        cols = st.columns([1.8, 2.05, 1.35, 2.05])
        with cols[0]:
            preview = "、".join(st.session_state["selected_cities"][:3])
            suffix = "等" if len(st.session_state["selected_cities"]) > 3 else ""
            st.markdown(
                f"<div class='filter-label city-filter-card'>当前监控城市：<span class='city-count'>{len(st.session_state['selected_cities'])} 个</span><br><span style='color:#6c82a1;font-weight:700;'>{html.escape(preview + suffix)}</span></div>",
                unsafe_allow_html=True,
            )
            if st.button("管理城市", type="primary", use_container_width=True):
                open_city_manager()
        with cols[1]:
            st.markdown("<div class='filter-label'>选择日期：</div>", unsafe_allow_html=True)
            date_col = st.columns(3)
            for col, (label, short, key) in zip(date_col, DATE_OPTIONS):
                with col:
                    st.button(
                        f"{label} {short}",
                        type="primary" if key == st.session_state["selected_date"] else "secondary",
                        disabled=key == st.session_state["selected_date"],
                        on_click=set_date,
                        args=(key,),
                        use_container_width=True,
                    )
        with cols[2]:
            st.markdown("<div class='filter-label'>风险筛选：</div>", unsafe_allow_html=True)
            selected = st.selectbox(
                "风险筛选",
                RISK_OPTIONS,
                index=RISK_OPTIONS.index(st.session_state["risk_filter"]),
                label_visibility="collapsed",
            )
            if selected != st.session_state["risk_filter"]:
                set_risk_filter(selected)
                st.rerun()
        with cols[3]:
            st.markdown("<div class='filter-label'>操作：</div>", unsafe_allow_html=True)
            btn_cols = st.columns(3)
            for col, label in zip(btn_cols, ["显示设置", "导出数据", "全屏查看"]):
                with col:
                    st.button(label, use_container_width=True)


def render_heatmap_table(df):
    """Render the 4 fixed metadata columns plus 24 hourly probability columns."""
    if df.empty:
        st.warning("当前筛选条件下没有可展示城市，请调整日期或风险筛选。")
        return

    header_cells = [
        "<th class='col-city'>城市</th>",
        "<th class='col-weather'>代表天气</th>",
        "<th class='col-max'>最高概率</th>",
        "<th class='col-window'>高风险窗口</th>",
    ]
    header_cells.extend(f"<th class='col-hour'>{hour}</th>" for hour in HOURS)

    body_rows = []
    for _, row in df.iterrows():
        cells = [
            f"<td class='city-cell'>{html.escape(row['city'])}</td>",
            f"<td class='weather-cell'>{weather_icon(row['weather'])}　{html.escape(row['weather'])}</td>",
            f"<td class='{max_class(row['max_prob'])}'>{int(row['max_prob'])}%</td>",
            f"<td class='window-cell'>{html.escape(row['risk_window'])}</td>",
        ]
        for hour in HOURS:
            value = int(row[hour])
            cells.append(f"<td class='{risk_class(value)}'>{value}%</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    table_html = (
        '<div class="table-card">'
        '<div class="table-heading">'
        "<div>"
        '<div class="table-title">城市24小时降雨概率预测（%）</div>'
        f'<div class="table-note">当前日期：{html.escape(st.session_state["selected_date"])}｜展示城市：{len(df)} 个</div>'
        "</div>"
        f'<div class="heatmap-legend legend-grid">{risk_legend_html()}</div>'
        "</div>"
        '<div class="table-wrap">'
        '<table class="rain-table">'
        f"<thead><tr>{''.join(header_cells)}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
        "</div>"
        "</div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


def render_bottom_panel(df):
    top5 = df.sort_values("max_prob", ascending=False).head(5)
    top5_html = "".join(
        (
            '<div class="rank-pill">'
            f'<span class="rank-no">{index}</span>'
            f"<span>{html.escape(row['city'])}</span>"
            f'<span class="rank-value">{int(row["max_prob"])}%</span>'
            "</div>"
        )
        for index, (_, row) in enumerate(top5.iterrows(), start=1)
    )
    bottom_html = (
        '<div class="bottom-panel">'
        '<div class="bottom-section">'
        '<div class="bottom-title">高风险城市TOP5（按最高概率）</div>'
        f'<div class="top5-grid">{top5_html}</div>'
        "</div>"
        '<div class="bottom-section">'
        '<div class="bottom-title">降雨概率图例（%）</div>'
        f'<div class="legend-grid">{risk_legend_html()}</div>'
        "</div>"
        '<div class="bottom-section">'
        '<div class="bottom-title">数据说明</div>'
        '<div class="data-copy">'
        "本产品基于 Open-Meteo 4.0 与和风天气 3.0 数据，采用多源融合算法生成未来72小时逐小时降雨概率预测。"
        "数据仅供参考，请结合实际情况合理安排出行与运营动作。"
        "</div>"
        "</div>"
        "</div>"
    )
    st.markdown(bottom_html, unsafe_allow_html=True)


def render_city_selector_content():
    catalog = load_city_catalog()
    if "city_manager_message" in st.session_state:
        st.warning(st.session_state.pop("city_manager_message"))

    keyword = st.text_input(
        "搜索中国地级市",
        placeholder="输入城市名，例如：嘉兴、福州、深圳、南平",
        key="city_search_keyword",
    ).strip()

    if keyword:
        search_columns = ["province", "city", "region", "tags"]
        search_mask = False
        for column in search_columns:
            search_mask = search_mask | catalog[column].fillna("").astype(str).str.contains(keyword, na=False, regex=False)
        filtered = catalog[search_mask].copy()
    else:
        default_pool = list(dict.fromkeys(DEFAULT_CITIES + pending_cities()))
        filtered = catalog[catalog["city"].isin(default_pool)].copy()

    result_col, selected_col = st.columns([1.05, 1], gap="medium")
    with result_col:
        st.markdown("**搜索结果**")
        if keyword:
            st.caption(f"在全国地级市城市池中找到 {len(filtered)} 个结果。")
        else:
            st.caption("输入城市名称即可搜索全国地级市。当前先展示默认城市。")

        if filtered.empty:
            st.info("没有找到匹配的地级市。")

        current_pending = pending_cities()
        replace_index = st.session_state.get("replace_city_index")
        for _, row in filtered.head(16).iterrows():
            city = row["city"]
            selected = city in current_pending
            available = str(row.get("location_id", "")).strip() != ""
            replacing_current = replace_index is not None and 0 <= replace_index < len(current_pending) and current_pending[replace_index] == city
            duplicate_for_replace = replace_index is not None and selected and not replacing_current
            entry_cols = st.columns([2.3, 0.9])
            with entry_cols[0]:
                tags = str(row.get("tags", "") or "").strip()
                st.markdown(
                    f"<div class='city-entry'><div class='city-entry-name'>{html.escape(city)}</div>"
                    f"<div class='city-entry-meta'>{html.escape(row['province'])}｜{html.escape(row['region'])}｜{html.escape(tags or '无标签')}</div></div>",
                    unsafe_allow_html=True,
                )
            with entry_cols[1]:
                if not available:
                    st.button("暂不可用", key=f"candidate_unavailable_{city}", disabled=True, use_container_width=True)
                elif replacing_current:
                    st.button("当前项", key=f"candidate_current_{city}", disabled=True, use_container_width=True)
                elif duplicate_for_replace or (selected and replace_index is None):
                    st.button("已选择", key=f"candidate_selected_{city}", disabled=True, use_container_width=True)
                elif replace_index is None and len(current_pending) >= MAX_DISPLAY_CITIES:
                    st.button("已满", key=f"candidate_full_{city}", disabled=True, use_container_width=True)
                else:
                    action_label = "替换为" if replace_index is not None else "添加"
                    if st.button(action_label, key=f"candidate_add_{city}", use_container_width=True):
                        add_pending_city(city)
                        rerun_app()

    with selected_col:
        pending = pending_cities()
        st.markdown(f"**当前已选城市 {len(pending)}/{MAX_DISPLAY_CITIES}**")
        st.caption("这里是临时选择，点击确认后才更新主看板并刷新数据。")
        selected_action_cols = st.columns(2)
        with selected_action_cols[0]:
            if st.button("清空", use_container_width=True):
                clear_pending_cities()
                rerun_app()
        with selected_action_cols[1]:
            if st.button("恢复默认", use_container_width=True):
                restore_default_pending()
                rerun_app()

        replace_index = st.session_state.get("replace_city_index")
        if replace_index is not None:
            st.info(f"正在替换第 {replace_index + 1} 个城市，请在搜索结果中选择新城市。")

        for index, city in enumerate(pending):
            row_cols = st.columns([1.7, 0.7, 0.7])
            with row_cols[0]:
                province = catalog.loc[catalog["city"] == city, "province"]
                province_text = province.iloc[0] if not province.empty else ""
                st.markdown(
                    f"<div class='selected-city-row'><div class='city-entry-name'>{index + 1}. {html.escape(city)}</div>"
                    f"<div class='city-entry-meta'>{html.escape(province_text)}</div></div>",
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("替换", key=f"city_replace_{city}_{index}", use_container_width=True):
                    replace_pending_city(index)
                    rerun_app()
            with row_cols[2]:
                if st.button("删除", key=f"city_remove_{city}_{index}", disabled=len(pending) <= 1, use_container_width=True):
                    remove_pending_city(city)
                    rerun_app()

        confirm_cols = st.columns([1, 1.2])
        with confirm_cols[0]:
            if st.button("取消", use_container_width=True):
                cancel_city_selection()
        with confirm_cols[1]:
            if st.button("确认应用城市", type="primary", disabled=not pending, use_container_width=True):
                confirm_city_selection()


if hasattr(st, "dialog"):
    @st.dialog("管理城市")
    def open_city_selector():
        render_city_selector_content()
else:
    def open_city_selector():
        with st.expander("管理城市", expanded=True):
            render_city_selector_content()


def main():
    page_config()
    inject_styles()
    initialize_state()
    cleaned_selected = clean_city_list(st.session_state["selected_cities"])
    if not cleaned_selected:
        cleaned_selected = list(DEFAULT_CITIES)
    st.session_state["selected_cities"] = cleaned_selected[:MAX_DISPLAY_CITIES]

    with st.spinner("正在准备城市降雨概率数据..."):
        selected_df = shifted_dataframe(st.session_state["selected_date"], st.session_state["selected_cities"])
        filtered_df = apply_risk_filter(selected_df, st.session_state["risk_filter"])

    render_header()
    render_summary_cards(selected_df)
    render_filter_bar()
    if st.session_state.get("show_city_selector"):
        open_city_selector()
    render_heatmap_table(filtered_df)
    render_bottom_panel(selected_df)


if __name__ == "__main__":
    main()
