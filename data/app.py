from __future__ import annotations

import streamlit as st

from components.city_manager import open_city_manager, render_city_manager
from components.layout import render_bottom_panel, render_header, render_heatmap_table, render_summary_cards
from services.city_service import MAX_DISPLAY_CITIES, clean_city_list, default_cities
from services.weather_service import DATE_OPTIONS, filter_by_risk, get_weather_data, summarize
from styles import inject_styles

RISK_OPTIONS = ["全部风险", "高风险", "中高风险", "中低风险", "低风险"]


def init_state() -> None:
    if "selected_cities" not in st.session_state:
        st.session_state.selected_cities = default_cities()
    cleaned = clean_city_list(st.session_state.selected_cities)
    st.session_state.selected_cities = cleaned[:MAX_DISPLAY_CITIES] if len(cleaned) >= MAX_DISPLAY_CITIES else default_cities()

    st.session_state.setdefault("pending_cities", st.session_state.selected_cities.copy())
    st.session_state.setdefault("selected_date", DATE_OPTIONS[0][2])
    st.session_state.setdefault("risk_filter", RISK_OPTIONS[0])
    st.session_state.setdefault("refresh_token", 0)
    st.session_state.setdefault("city_manager_open", False)
    st.session_state.setdefault("city_manager_notice", "")
    st.session_state.setdefault("replace_city_index", None)


def render_filter_bar() -> tuple[str, str, bool, bool]:
    selected = st.session_state.selected_cities
    preview = "、".join(selected[:4]) + (" 等" if len(selected) > 4 else "")
    with st.container(border=True):
        cols = st.columns([1.85, 1.0, 2.4, 1.45, 2.0], vertical_alignment="center")
        with cols[0]:
            st.markdown(
                f"<div class='filter-label'>当前监控城市：<span class='city-count'>{len(selected)} 个</span></div>"
                f"<div class='city-preview'>{preview}</div>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            manage_clicked = st.button("管理城市", type="primary", use_container_width=True)
        with cols[2]:
            st.markdown("<div class='filter-label'>选择日期：</div>", unsafe_allow_html=True)
            date_cols = st.columns(3)
            selected_date = st.session_state.selected_date
            for col, (label, short, key) in zip(date_cols, DATE_OPTIONS):
                with col:
                    if st.button(
                        f"{label} {short}",
                        type="primary" if key == selected_date else "secondary",
                        disabled=key == selected_date,
                        use_container_width=True,
                    ):
                        selected_date = key
        with cols[3]:
            st.markdown("<div class='filter-label'>风险筛选：</div>", unsafe_allow_html=True)
            risk_filter = st.selectbox(
                "风险筛选",
                RISK_OPTIONS,
                index=RISK_OPTIONS.index(st.session_state.risk_filter),
                label_visibility="collapsed",
            )
        with cols[4]:
            st.markdown("<div class='filter-label'>操作：</div>", unsafe_allow_html=True)
            action_cols = st.columns(3)
            with action_cols[0]:
                st.button("显示设置", use_container_width=True)
            with action_cols[1]:
                st.button("导出数据", use_container_width=True)
            with action_cols[2]:
                refresh_clicked = st.button("刷新数据", use_container_width=True)
    return selected_date, risk_filter, manage_clicked, refresh_clicked


def main() -> None:
    st.set_page_config(
        page_title="城市72小时降雨概率雷达",
        page_icon="☔",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    init_state()

    with st.spinner("正在加载15个城市的分小时降雨概率..."):
        weather_df, warnings, updated_at = get_weather_data(
            tuple(st.session_state.selected_cities),
            st.session_state.selected_date,
            st.session_state.refresh_token,
        )

    render_header(updated_at)
    if warnings:
        with st.expander("数据源降级提示", expanded=False):
            for message in warnings[:20]:
                st.caption(message)

    if weather_df.empty:
        st.error("当前城市均未获取到可用天气数据，请检查城市池、API 配置或稍后刷新。")
        if st.button("管理城市", type="primary"):
            open_city_manager()
            st.rerun()
        render_city_manager()
        return

    summary = summarize(weather_df)
    render_summary_cards(summary, updated_at)
    selected_date, risk_filter, manage_clicked, refresh_clicked = render_filter_bar()

    if selected_date != st.session_state.selected_date:
        st.session_state.selected_date = selected_date
        st.rerun()
    if risk_filter != st.session_state.risk_filter:
        st.session_state.risk_filter = risk_filter
        st.rerun()
    if manage_clicked:
        open_city_manager()
        st.rerun()
    if refresh_clicked:
        st.session_state.refresh_token += 1
        st.rerun()

    filtered_df = filter_by_risk(weather_df, st.session_state.risk_filter)
    render_heatmap_table(filtered_df, st.session_state.selected_date)
    render_bottom_panel(weather_df)
    render_city_manager()


if __name__ == "__main__":
    main()

