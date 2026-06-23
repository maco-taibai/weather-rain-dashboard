from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from services.weather_service import HOURS


def probability_class(value: int) -> str:
    if value >= 80:
        return "risk-extreme"
    if value >= 60:
        return "risk-high"
    if value >= 30:
        return "risk-mid"
    return "risk-low"


def max_class(value: int) -> str:
    if value >= 80:
        return "max-extreme"
    if value >= 60:
        return "max-high"
    if value >= 30:
        return "max-mid"
    return "max-low"


def weather_icon(weather: str) -> str:
    if "雷" in weather:
        return "⛈"
    if "雨" in weather or "毛毛" in weather:
        return "☔"
    if "晴" in weather:
        return "☀"
    return "☁"


def render_header(updated_at: str) -> None:
    st.markdown(
        f"""
        <div class="topbar">
          <div class="brand">
            <div class="brand-icon">☔</div>
            <div>
              <div class="brand-title">城市72小时降雨概率雷达</div>
              <div class="brand-sub">72小时监测</div>
            </div>
          </div>
          <div class="service">
            <span>气象数据服务中心</span>
            <span>更新时间：{html.escape(updated_at)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_cards(summary: dict, updated_at: str) -> None:
    top_city = html.escape(str(summary.get("top_city", "--")))
    top_prob = int(summary.get("top_prob", 0) or 0)
    high_count = int(summary.get("high_count", 0) or 0)
    high_cities = html.escape(str(summary.get("high_cities", "暂无")))
    peak_window = html.escape(str(summary.get("peak_window", "--")))
    sources = html.escape(str(summary.get("sources", "Open-Meteo 4.0、和风天气 3.0、WeatherAPI 3.0")))
    st.markdown(
        f"""
        <div class="summary-grid">
          <div class="summary-card">
            <div class="summary-icon">✓</div>
            <div><div class="summary-label">最高风险城市</div><div class="summary-value">{top_city}　<span class="danger">{top_prob}%</span></div></div>
          </div>
          <div class="summary-card">
            <div class="summary-icon orange">!</div>
            <div><div class="summary-label">高风险城市数</div><div class="summary-value orange-text">{high_count} 个</div><div class="summary-hint">{high_cities}</div></div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">◷</div>
            <div><div class="summary-label">风险高峰时段</div><div class="summary-value blue-text">{peak_window}</div><div class="summary-hint">未来72小时内风险最集中的时段</div></div>
          </div>
          <div class="summary-card">
            <div class="summary-icon cyan">▧</div>
            <div><div class="summary-label">数据更新时间 / 数据源</div><div class="summary-value small">{html.escape(updated_at)}</div><div class="summary-hint">数据源：{sources}</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_heatmap_table(df: pd.DataFrame, date_key: str) -> None:
    if df.empty:
        st.warning("当前没有可展示的城市数据，请检查城市选择或稍后刷新。")
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
        max_prob = int(row.get("max_prob", 0) or 0)
        cells = [
            f"<td class='city-cell'>{html.escape(str(row.get('city', '')))}</td>",
            f"<td class='weather-cell'>{weather_icon(str(row.get('weather', '')))}　{html.escape(str(row.get('weather', '--')))}</td>",
            f"<td class='{max_class(max_prob)}'>{max_prob}%</td>",
            f"<td class='window-cell'>{html.escape(str(row.get('risk_window', '--')))}</td>",
        ]
        for hour in HOURS:
            value = int(row.get(hour, 0) or 0)
            title = f"{row.get('city', '')} {hour}:00｜{row.get('weather', '--')}｜降雨概率 {value}%"
            cells.append(f"<td class='{probability_class(value)}' title='{html.escape(title)}'>{value}%</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    st.markdown(
        (
            '<div class="table-card">'
            '<div class="table-heading">'
            '<div class="table-title">15个城市24小时降雨概率预测（%）</div>'
            f'<div class="table-note">当前日期：{html.escape(date_key)}｜展示城市：{len(df)} 个</div>'
            "</div>"
            '<div class="table-wrap"><table class="rain-table">'
            f"<thead><tr>{''.join(header_cells)}</tr></thead><tbody>{''.join(body_rows)}</tbody>"
            "</table></div></div>"
        ),
        unsafe_allow_html=True,
    )


def render_bottom_panel(df: pd.DataFrame) -> None:
    if df.empty:
        return
    top5 = df.sort_values("max_prob", ascending=False).head(5)
    top5_html = "".join(
        f'<div class="rank-pill"><span class="rank-no">{index}</span><span>{html.escape(str(row["city"]))}</span><span class="rank-value">{int(row["max_prob"])}%</span></div>'
        for index, (_, row) in enumerate(top5.iterrows(), start=1)
    )
    st.markdown(
        f"""
        <div class="bottom-panel">
          <div class="bottom-section">
            <div class="bottom-title">高风险城市TOP5（按最高概率）</div>
            <div class="top5-grid">{top5_html}</div>
          </div>
          <div class="bottom-section">
            <div class="bottom-title">降雨概率图例（%）</div>
            <div class="legend-grid">
              <div class="legend-item"><span class="swatch risk-low"></span><span>0-29%　低概率</span></div>
              <div class="legend-item"><span class="swatch risk-mid"></span><span>30-59%　中等概率</span></div>
              <div class="legend-item"><span class="swatch risk-high"></span><span>60-79%　较高概率</span></div>
              <div class="legend-item"><span class="swatch risk-extreme"></span><span>≥80%　高风险</span></div>
            </div>
          </div>
          <div class="bottom-section">
            <div class="bottom-title">数据说明</div>
            <div class="data-copy">本产品基于 Open-Meteo 4.0、和风天气 3.0 与 WeatherAPI 3.0 数据，采用 4:3:3 多源融合算法生成未来72小时逐小时降雨概率预测。数据仅供参考，请结合实际情况合理安排出行与运营动作。</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

