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
        filtered = catalog[catalog["city"].str.contains(keyword, na=False, regex=False)].copy()
    else:
        default_pool = list(dict.fromkeys(DEFAULT_CITIES + pending_cities()))
        filtered = catalog[catalog["city"].isin(default_pool)].copy()

    result_col, selected_col = st.columns([1.25, 1])
    with result_col:
        st.markdown("**搜索结果**")
        if keyword:
            st.caption(f"在全国地级市城市池中找到 {len(filtered)} 个结果。")
        else:
            st.caption("输入城市名称即可搜索全国地级市。当前先展示默认城市。")

        if filtered.empty:
            st.info("没有找到匹配的地级市。")

        for _, row in filtered.head(30).iterrows():
            city = row["city"]
            selected = city in pending_cities()
            available = str(row.get("location_id", "")).strip() != ""
            entry_cols = st.columns([2.3, 0.9])
            with entry_cols[0]:
                st.markdown(
                    f"<div class='city-entry'><div class='city-entry-name'>{html.escape(city)}</div>"
                    f"<div class='city-entry-meta'>{html.escape(row['province'])}｜{html.escape(row['region'])}｜{html.escape(str(row['tags']) or '无标签')}</div></div>",
                    unsafe_allow_html=True,
                )
            with entry_cols[1]:
                if not available:
                    st.button("暂不可用", key=f"candidate_unavailable_{city}", disabled=True, use_container_width=True)
                elif selected:
                    st.button("已选择", key=f"candidate_selected_{city}", disabled=True, use_container_width=True)
                else:
                    if st.button("添加", key=f"candidate_add_{city}", use_container_width=True):
                        add_pending_city(city)
                        st.rerun()

    with selected_col:
        pending = pending_cities()
        st.markdown(f"**当前已选城市 {len(pending)}/{MAX_DISPLAY_CITIES}**")
        st.caption("这里是临时选择，点击确认后才更新主看板并刷新数据。")
        selected_action_cols = st.columns(2)
        with selected_action_cols[0]:
            if st.button("清空", use_container_width=True):
                clear_pending_cities()
                st.rerun()
        with selected_action_cols[1]:
            if st.button("恢复默认", use_container_width=True):
                restore_default_pending()
                st.rerun()

        replace_index = st.session_state.get("replace_city_index")
        if replace_index is not None:
            st.info(f"正在替换第 {replace_index + 1} 个城市，请在中间候选列表选择新城市。")

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
                    st.rerun()
            with row_cols[2]:
                if st.button("删除", key=f"city_remove_{city}_{index}", disabled=len(pending) <= 1, use_container_width=True):
                    remove_pending_city(city)
                    st.rerun()

        confirm_cols = st.columns([1, 1.2])
        with confirm_cols[0]:
            st.button("取消", on_click=cancel_city_selection, use_container_width=True)
        with confirm_cols[1]:
            st.button("确认应用城市", type="primary", on_click=confirm_city_selection, use_container_width=True)


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
    cleaned_selected = clean_city_list(st.session_state["selected_cities"])
    if not cleaned_selected:
        cleaned_selected = list(DEFAULT_CITIES)
    st.session_state["selected_cities"] = cleaned_selected[:MAX_DISPLAY_CITIES]

    selected_df = shifted_dataframe(st.session_state["selected_date"], st.session_state["selected_cities"])
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
