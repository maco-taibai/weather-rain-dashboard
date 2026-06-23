import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --blue: #1677ff;
            --blue-dark: #0d3470;
            --text: #14345f;
            --muted: #5e7395;
            --line: #dbe8f6;
            --panel: rgba(255, 255, 255, 0.94);
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
                radial-gradient(circle at 18% 0%, rgba(255,255,255,.96), rgba(255,255,255,0) 24%),
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
        div[data-testid="stVerticalBlock"] { gap: .75rem; }
        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 10px;
        }
        .brand { display: flex; align-items: center; gap: 14px; min-width: 0; }
        .brand-icon {
            width: 44px; height: 44px; border-radius: 14px; display: grid; place-items: center;
            background: #e9f4ff; color: var(--blue); font-size: 25px;
            box-shadow: inset 0 0 0 1px rgba(22,119,255,.14);
        }
        .brand-title {
            font-size: 28px; line-height: 1.1; color: #0f3267; font-weight: 850; letter-spacing: 0;
        }
        .brand-sub {
            display: inline-flex; align-items: center; height: 22px; margin-top: 6px; padding: 0 9px;
            border-radius: 999px; background: #eaf4ff; color: #2b6db8; font-size: 12px; font-weight: 800;
        }
        .service {
            display: flex; align-items: center; gap: 12px; color: #385883; font-weight: 800; white-space: nowrap;
        }
        .summary-grid {
            display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 12px;
        }
        .summary-card {
            min-height: 108px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel);
            box-shadow: 0 12px 28px rgba(29,89,143,.08); padding: 18px 20px;
            display: flex; align-items: center; gap: 16px;
        }
        .summary-icon {
            width: 54px; height: 54px; border-radius: 50%; display: grid; place-items: center;
            background: #f1f7ff; color: var(--blue); font-size: 24px; flex: 0 0 auto;
        }
        .summary-icon.orange { color: #ff6b00; background: #fff4ec; }
        .summary-icon.cyan { color: #5fb8c0; background: #eefbfc; }
        .summary-label { color: #244b7d; font-size: 14px; font-weight: 850; margin-bottom: 8px; }
        .summary-value { color: #0f3c78; font-size: 25px; font-weight: 900; line-height: 1.1; }
        .summary-value .danger, .danger { color: #f00636; }
        .summary-value.small { font-size: 21px; }
        .orange-text { color: #ff6b00; }
        .blue-text { color: var(--blue); }
        .summary-hint {
            margin-top: 8px; color: #6680a3; font-size: 12px; font-weight: 700;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .filter-label { color: #254c7d; font-size: 13px; font-weight: 850; margin-bottom: 7px; white-space: nowrap; }
        .city-count { color: #1d5fae; font-weight: 900; }
        .city-preview {
            color: #6c82a1; font-size: 12px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .table-card {
            border: 1px solid var(--line); border-radius: 8px; background: rgba(255,255,255,.96);
            box-shadow: 0 14px 32px rgba(29,89,143,.08); padding: 14px;
        }
        .table-heading { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px; }
        .table-title { color: #0f3267; font-size: 21px; font-weight: 900; }
        .table-note { color: #627a9e; font-size: 12px; font-weight: 750; }
        .table-wrap { overflow-x: auto; border: 1px solid #dce8f5; border-radius: 6px; background: white; }
        .rain-table { width: 100%; min-width: 1560px; border-collapse: separate; border-spacing: 0; table-layout: fixed; font-size: 13px; }
        .rain-table th {
            height: 36px; background: #f3f8fe; color: #143d72; border-bottom: 1px solid #dce8f5;
            border-right: 1px solid #e6eef8; font-weight: 900; white-space: nowrap;
        }
        .rain-table td {
            height: 31px; text-align: center; border-bottom: 1px solid #edf2f8; border-right: 1px solid #edf2f8;
            font-weight: 850; white-space: nowrap;
        }
        .col-city { width: 84px; }
        .col-weather { width: 92px; }
        .col-max { width: 86px; }
        .col-window { width: 102px; }
        .col-hour { width: 46px; }
        .city-cell { color: #10386f; text-align: left !important; padding-left: 12px; background: #fbfdff; }
        .weather-cell, .window-cell { color: #385d8c; background: #fbfdff; }
        .rain-table .col-city, .rain-table .city-cell { position: sticky; left: 0; z-index: 4; }
        .rain-table .col-weather, .rain-table .weather-cell { position: sticky; left: 84px; z-index: 4; }
        .rain-table .col-max, .rain-table td:nth-child(3) { position: sticky; left: 176px; z-index: 4; background-clip: padding-box; }
        .rain-table .col-window, .rain-table .window-cell { position: sticky; left: 262px; z-index: 4; }
        .rain-table th.col-city, .rain-table th.col-weather, .rain-table th.col-max, .rain-table th.col-window { z-index: 5; }
        .max-low { color: var(--green-text); background: #fbfdff; }
        .max-mid { color: var(--yellow-text); background: #fbfdff; }
        .max-high { color: var(--orange-text); background: #fbfdff; }
        .max-extreme { color: #f00636; background: #fbfdff; }
        .risk-low { background: var(--green-bg); color: var(--green-text); }
        .risk-mid { background: var(--yellow-bg); color: var(--yellow-text); }
        .risk-high { background: var(--orange-bg); color: var(--orange-text); }
        .risk-extreme { background: var(--red-bg); color: var(--red-text); }
        .bottom-panel {
            display: grid; grid-template-columns: 1.05fr .85fr 1.3fr; gap: 20px; border: 1px solid var(--line);
            border-radius: 8px; background: rgba(255,255,255,.94); box-shadow: 0 10px 24px rgba(29,89,143,.06);
            padding: 18px 20px; margin-top: 12px;
        }
        .bottom-section { min-width: 0; border-right: 1px solid #dce8f5; padding-right: 20px; }
        .bottom-section:last-child { border-right: none; padding-right: 0; }
        .bottom-title { color: #0f3267; font-size: 16px; font-weight: 900; margin-bottom: 12px; }
        .top5-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
        .rank-pill {
            display: inline-flex; align-items: center; gap: 8px; min-height: 30px; border-radius: 999px;
            border: 1px solid #f3d7d7; background: #fffafa; padding: 4px 10px 4px 5px;
            color: #153a70; font-size: 13px; font-weight: 900;
        }
        .rank-no {
            width: 22px; height: 22px; border-radius: 50%; display: inline-grid; place-items: center;
            background: #ff6d7d; color: #fff; font-size: 12px; flex: 0 0 auto;
        }
        .rank-value { color: #f00636; margin-left: auto; }
        .legend-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 22px; }
        .legend-item { display: flex; align-items: center; gap: 10px; color: #385d8c; font-size: 13px; font-weight: 800; }
        .swatch { width: 34px; height: 16px; border-radius: 5px; border: 1px solid rgba(0,0,0,.04); }
        .data-copy { color: #4f6990; font-size: 13px; line-height: 1.8; font-weight: 700; }
        .stButton > button {
            border-radius: 7px; border: 1px solid #cdddf0; color: #244b7d; background: #f8fbff; font-weight: 850;
        }
        .stButton > button[kind="primary"] { background: var(--blue); border-color: var(--blue); color: #fff; }
        div[data-testid="stDialog"] div[role="dialog"] { border-radius: 10px; max-width: 1280px; width: 92vw; }
        .selected-city-row {
            border: 1px solid #dbe8f6; background: #ffffff; border-radius: 8px; padding: 8px; margin-bottom: 8px;
        }
        .city-manager-help {
            color: #5a7398; font-size: 13px; line-height: 1.75; font-weight: 700;
            border: 1px solid #dbe8f6; border-radius: 8px; background: #f8fbff; padding: 14px;
        }
        @media (max-width: 1200px) {
            .summary-grid, .bottom-panel { grid-template-columns: 1fr; }
            .bottom-section { border-right: none; border-bottom: 1px solid #dce8f5; padding-right: 0; padding-bottom: 14px; }
            .topbar { flex-direction: column; align-items: flex-start; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

