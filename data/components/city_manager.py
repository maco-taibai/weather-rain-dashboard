from __future__ import annotations

import html

import streamlit as st

from services.city_service import MAX_DISPLAY_CITIES, default_cities, load_city_pool, search_cities


def open_city_manager() -> None:
    st.session_state.pending_cities = st.session_state.selected_cities.copy()
    st.session_state.replace_city_index = None
    st.session_state.city_manager_notice = ""
    st.session_state.city_manager_open = True


def _add_or_replace_city(city: str) -> None:
    pending = st.session_state.pending_cities
    replace_index = st.session_state.get("replace_city_index")
    if replace_index is not None and 0 <= replace_index < len(pending):
        if city in pending and pending[replace_index] != city:
            st.session_state.city_manager_notice = "该城市已在当前列表中，不能重复选择。"
            return
        old_city = pending[replace_index]
        pending[replace_index] = city
        st.session_state.replace_city_index = None
        st.session_state.city_manager_notice = f"已将 {old_city} 替换为 {city}，点击应用后刷新看板。"
        return

    if city in pending:
        st.session_state.city_manager_notice = "该城市已存在。"
        return
    if len(pending) >= MAX_DISPLAY_CITIES:
        st.session_state.city_manager_notice = "当前看板最多支持15个城市，请先删除或使用替换。"
        return
    pending.append(city)
    st.session_state.city_manager_notice = f"已添加 {city}，点击应用后刷新看板。"


def _remove_city(index: int) -> None:
    pending = st.session_state.pending_cities
    if 0 <= index < len(pending):
        removed = pending.pop(index)
        st.session_state.replace_city_index = None
        st.session_state.city_manager_notice = f"已删除 {removed}，请补足15个城市后应用。"


def _move_city(index: int, direction: int) -> None:
    pending = st.session_state.pending_cities
    target = index + direction
    if 0 <= index < len(pending) and 0 <= target < len(pending):
        pending[index], pending[target] = pending[target], pending[index]
        replace_index = st.session_state.get("replace_city_index")
        if replace_index == index:
            st.session_state.replace_city_index = target
        elif replace_index == target:
            st.session_state.replace_city_index = index


def _render_body() -> None:
    st.markdown("#### 监控城市管理")
    st.caption("推荐使用“替换”：先点中间某个城市的替换，再在左侧搜索新城市。点击应用前不会刷新天气数据。")
    left, middle, right = st.columns([1.25, 1.55, 1.0], gap="large")

    with left:
        st.markdown("**搜索全国地级市**")
        replace_index = st.session_state.get("replace_city_index")
        if replace_index is not None and replace_index < len(st.session_state.pending_cities):
            replacing = st.session_state.pending_cities[replace_index]
            st.info(f"正在替换：{replacing}")
            if st.button("取消替换", use_container_width=True):
                st.session_state.replace_city_index = None
                st.rerun()

        keyword = st.text_input("请输入城市名称", key="city_search_keyword", placeholder="例如：长春、嘉兴、佛山、福州")
        results = search_cities(keyword, limit=24)
        if keyword and not results:
            st.warning("未找到该城市。")
        for item in results:
            city = item["city"]
            replace_index = st.session_state.get("replace_city_index")
            pending = st.session_state.pending_cities
            replacing_current = replace_index is not None and replace_index < len(pending) and pending[replace_index] == city
            duplicate_for_replace = replace_index is not None and city in pending and not replacing_current
            disabled = duplicate_for_replace or (replace_index is None and (city in pending or len(pending) >= MAX_DISPLAY_CITIES))
            action = "替换为" if replace_index is not None else "添加"
            label = f"{action} {city}｜{item.get('province', '')}"
            if st.button(label, key=f"candidate_{city}", disabled=disabled, use_container_width=True):
                _add_or_replace_city(city)
                st.rerun()
        if len(st.session_state.pending_cities) >= MAX_DISPLAY_CITIES and st.session_state.get("replace_city_index") is None:
            st.info("当前已满15个城市。建议点击中间列表中的“替换”。")

    with middle:
        pending = st.session_state.pending_cities
        st.markdown(f"**待应用城市：{len(pending)}/15**")
        if len(pending) != MAX_DISPLAY_CITIES:
            st.warning("请保持15个城市后再应用。")
        for index, city in enumerate(pending):
            is_replacing = st.session_state.get("replace_city_index") == index
            st.markdown('<div class="selected-city-row">', unsafe_allow_html=True)
            cols = st.columns([1.6, 0.62, 0.62, 0.62, 0.62], vertical_alignment="center")
            with cols[0]:
                label = f"{index + 1}. {city}"
                if is_replacing:
                    label += "  ← 正在替换"
                st.write(label)
            with cols[1]:
                if st.button("替换", key=f"replace_{index}", disabled=is_replacing, use_container_width=True):
                    st.session_state.replace_city_index = index
                    st.session_state.city_manager_notice = f"正在替换 {city}，请在左侧搜索新城市。"
                    st.rerun()
            with cols[2]:
                if st.button("上移", key=f"up_{index}", disabled=index == 0, use_container_width=True):
                    _move_city(index, -1)
                    st.rerun()
            with cols[3]:
                if st.button("下移", key=f"down_{index}", disabled=index == len(pending) - 1, use_container_width=True):
                    _move_city(index, 1)
                    st.rerun()
            with cols[4]:
                if st.button("删除", key=f"remove_{index}", use_container_width=True):
                    _remove_city(index)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            f"""
            <div class="city-manager-help">
              <strong>操作说明</strong><br>
              当前已选：{len(st.session_state.pending_cities)}/15<br>
              搜索、删除、新增、排序期间不会请求天气 API<br>
              只有点击应用后才统一刷新三源天气数据<br>
              不足15个城市时应用按钮不可点击
            </div>
            """,
            unsafe_allow_html=True,
        )
        notice = st.session_state.get("city_manager_notice")
        if notice:
            st.info(notice)
        st.markdown("**城市池状态**")
        catalog = load_city_pool()
        st.caption(f"当前城市池：{len(catalog)} 个地级市")

    st.divider()
    cancel_col, restore_col, apply_col = st.columns([1, 1, 1])
    with cancel_col:
        if st.button("取消", use_container_width=True):
            st.session_state.pending_cities = st.session_state.selected_cities.copy()
            st.session_state.replace_city_index = None
            st.session_state.city_manager_open = False
            st.rerun()
    with restore_col:
        if st.button("恢复默认15城", use_container_width=True):
            st.session_state.pending_cities = default_cities()
            st.session_state.replace_city_index = None
            st.session_state.city_manager_notice = "已恢复默认15城，点击应用后刷新看板。"
            st.rerun()
    with apply_col:
        disabled = len(st.session_state.pending_cities) != MAX_DISPLAY_CITIES
        if st.button("应用并刷新看板", type="primary", disabled=disabled, use_container_width=True):
            st.session_state.selected_cities = st.session_state.pending_cities.copy()
            st.session_state.refresh_token = st.session_state.get("refresh_token", 0) + 1
            st.session_state.replace_city_index = None
            st.session_state.city_manager_open = False
            st.rerun()


def render_city_manager() -> None:
    if not st.session_state.get("city_manager_open", False):
        return
    if hasattr(st, "dialog"):
        @st.dialog("监控城市管理")
        def _dialog():
            _render_body()

        _dialog()
    else:
        with st.expander("监控城市管理", expanded=True):
            _render_body()

