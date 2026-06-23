import html

import pandas as pd
import streamlit as st


HOURS = [f"{hour:02d}" for hour in range(24)]
DATE_OPTIONS = [
    ("今天", "06-23", "2026-06-23"),
    ("明天", "06-24", "2026-06-24"),
    ("后天", "06-25", "2026-06-25"),
]
RISK_OPTIONS = ["全部风险", "高风险", "中高风险", "中低风险", "低风险"]

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
            padding: 18px 26px 22px;
        }

        header[data-testid="stHeader"],
        #MainMenu,
        footer,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stDeployButton"],
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
            white-space: nowrap;
        }

        .city-count {
            color: #1d5fae;
            font-weight: 900;
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


def shifted_dataframe(date_key):
    """Create lightweight mock variants for today, tomorrow, and the day after."""
    base = build_base_dataframe()
    offsets = {"2026-06-23": 0, "2026-06-24": -7, "2026-06-25": 5}
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
    cities = [row[0] for row in MOCK_ROWS]
    st.session_state.setdefault("selected_cities", cities)
    st.session_state.setdefault("draft_cities", list(st.session_state["selected_cities"]))
    st.session_state.setdefault("selected_date", DATE_OPTIONS[0][2])
    st.session_state.setdefault("risk_filter", RISK_OPTIONS[0])


def render_header():
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
        "<span>更新时间：2026-06-23 01:37</span>"
        '<button class="refresh-btn">刷新数据</button>'
        "</div>"
        "</div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)


def render_summary_cards(df):
    high_df = df[df["max_prob"] >= 80].sort_values("max_prob", ascending=False)
    top = df.sort_values("max_prob", ascending=False).iloc[0]
    high_names = "、".join(high_df["city"].tolist()) or "暂无"

    cards = [
        ("🛡", "最高风险城市", f"{top['city']}　{int(top['max_prob'])}%", f"最高时段：{top['risk_window']}", "danger"),
        ("🛡", "高风险城市数", f"{len(high_df)} 个", high_names, ""),
        ("◷", "风险高峰时段", "09:00 - 11:00", "未来72小时内风险最集中的时段", ""),
        ("▧", "数据更新时间 / 数据源", "2026-06-23 01:37", "数据源：Open-Meteo 4.0、和风天气 3.0", ""),
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
        cols = st.columns([1.45, 2.15, 1.35, 2.1])
        with cols[0]:
            st.markdown(
                f"<div class='filter-label'>当前城市：<span class='city-count'>{len(st.session_state['selected_cities'])} 个</span></div>",
                unsafe_allow_html=True,
            )
            if st.button("管理城市", type="primary", use_container_width=True):
                st.session_state["draft_cities"] = list(st.session_state["selected_cities"])
                open_city_selector()
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
        '<div class="table-title">15个城市24小时降雨概率预测（%）</div>'
        f'<div class="table-note">当前日期：{html.escape(st.session_state["selected_date"])}｜展示城市：{len(df)} 个</div>'
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
    legend_html = "".join(
        (
            '<div class="legend-item">'
            f'<span class="swatch {css_class}"></span>'
            f"<span>{html.escape(label)}</span>"
            "</div>"
        )
        for css_class, label in [
            ("risk-low", "0-29%　低概率"),
            ("risk-mid", "30-59%　中等概率"),
            ("risk-high", "60-79%　较高概率"),
            ("risk-extreme", "≥80%　高风险"),
        ]
    )

    bottom_html = (
        '<div class="bottom-panel">'
        '<div class="bottom-section">'
        '<div class="bottom-title">高风险城市TOP5（按最高概率）</div>'
        f'<div class="top5-grid">{top5_html}</div>'
        "</div>"
        '<div class="bottom-section">'
        '<div class="bottom-title">降雨概率图例（%）</div>'
        f'<div class="legend-grid">{legend_html}</div>'
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


def confirm_city_selection():
    if not st.session_state["draft_cities"]:
        st.warning("请至少选择一个城市。")
        return
    st.session_state["selected_cities"] = list(st.session_state["draft_cities"])
    st.rerun()


def cancel_city_selection():
    st.session_state["draft_cities"] = list(st.session_state["selected_cities"])
    st.rerun()


def render_city_selector_content():
    all_cities = [row[0] for row in MOCK_ROWS]
    provinces = ["全部省份"] + sorted(set(CITY_PROVINCES.values()))
    province = st.selectbox("按省份筛选", provinces)
    keyword = st.text_input("搜索城市", placeholder="输入城市名称，例如：上海、杭州、宁波").strip()

    filtered = all_cities
    if province != "全部省份":
        filtered = [city for city in filtered if CITY_PROVINCES.get(city) == province]
    if keyword:
        filtered = [city for city in filtered if keyword in city]

    current_draft = [city for city in st.session_state["draft_cities"] if city in all_cities]
    visible_options = list(dict.fromkeys(current_draft + filtered))
    st.multiselect(
        "多选城市",
        visible_options,
        key="draft_cities",
        format_func=lambda city: f"{city}（{CITY_PROVINCES.get(city, '')}）",
        placeholder="选择需要展示的城市",
    )
    st.caption(f"已预选 {len(st.session_state['draft_cities'])} 个城市；点击确认后才会更新主看板。")

    action_cols = st.columns([1, 1, 1.3])
    with action_cols[0]:
        st.button("取消", on_click=cancel_city_selection, use_container_width=True)
    with action_cols[1]:
        if st.button("恢复默认15城", use_container_width=True):
            st.session_state["draft_cities"] = all_cities
            st.rerun()
    with action_cols[2]:
        st.button("确认", type="primary", on_click=confirm_city_selection, use_container_width=True)


if hasattr(st, "dialog"):
    @st.dialog("管理城市")
    def open_city_selector():
        render_city_selector_content()
else:
    def open_city_selector():
        st.session_state["show_city_selector"] = True


def main():
    page_config()
    inject_styles()
    initialize_state()

    selected_df = shifted_dataframe(st.session_state["selected_date"])
    selected_df = selected_df[selected_df["city"].isin(st.session_state["selected_cities"])]
    filtered_df = apply_risk_filter(selected_df, st.session_state["risk_filter"])

    render_header()
    render_summary_cards(selected_df)
    render_filter_bar()
    if st.session_state.get("show_city_selector"):
        with st.expander("管理城市", expanded=True):
            render_city_selector_content()
    render_heatmap_table(filtered_df)
    render_bottom_panel(selected_df)


if __name__ == "__main__":
    main()
