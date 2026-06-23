from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
CITY_POOL_PATH = BASE_DIR / "data" / "china_city_pool.csv"
LEGACY_CITY_POOL_PATH = BASE_DIR / "data" / "china_city_locations.csv"
MAX_DISPLAY_CITIES = 15

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

KEYWORD_GROUPS = {
    "长三角": ["上海市", "杭州市", "宁波市", "苏州市", "南京市", "无锡市", "嘉兴市"],
    "珠三角": ["广州市", "深圳市", "佛山市", "东莞市", "珠海市", "惠州市", "中山市"],
    "华东": ["上海市", "杭州市", "南京市", "苏州市", "无锡市", "宁波市", "嘉兴市", "福州市", "厦门市"],
    "华南": ["广州市", "深圳市", "佛山市", "东莞市", "珠海市", "南宁市", "海口市"],
    "重点经营": ["佛山市", "莆田市", "遵义市", "大同市", "盐城市", "嘉兴市"],
}


@st.cache_data(show_spinner=False)
def load_city_pool() -> pd.DataFrame:
    source = CITY_POOL_PATH if CITY_POOL_PATH.exists() else LEGACY_CITY_POOL_PATH
    if not source.exists():
        return pd.DataFrame(columns=["province", "city", "city_code", "location_id", "lat", "lon", "region", "city_level", "tags"])

    df = pd.read_csv(source, dtype={"city_code": str, "location_id": str})
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
        if column not in df.columns:
            df[column] = default

    df = df[list(defaults.keys())].copy()
    text_columns = ["province", "city", "city_code", "location_id", "region", "city_level", "tags"]
    for column in text_columns:
        df[column] = df[column].fillna("").astype(str).str.strip()
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df[df["city"] != ""].drop_duplicates(subset=["city"]).reset_index(drop=True)
    return df


def normalize_city_name(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.endswith(("市", "州", "盟", "地区")):
        return value
    return f"{value}市"


def get_city_record(city_name: str) -> dict | None:
    normalized = normalize_city_name(city_name)
    if not normalized:
        return None
    df = load_city_pool()
    matched = df[df["city"] == normalized]
    if matched.empty:
        return None
    return matched.iloc[0].to_dict()


def search_cities(keyword: str, limit: int = 30) -> list[dict]:
    df = load_city_pool()
    keyword = (keyword or "").strip()
    if not keyword:
        return df.head(limit).to_dict("records")

    normalized = normalize_city_name(keyword)
    mask = pd.Series(False, index=df.index)
    for column in ["city", "province", "region", "tags"]:
        text = df[column].fillna("").astype(str)
        mask = mask | text.str.contains(keyword, na=False, regex=False) | text.str.contains(normalized, na=False, regex=False)
    return df[mask].head(limit).to_dict("records")


def valid_city_names() -> set[str]:
    df = load_city_pool()
    usable = df[(df["location_id"].fillna("").astype(str).str.strip() != "") & df["lat"].notna() & df["lon"].notna()]
    return set(usable["city"].tolist())


def clean_city_list(cities: list[str]) -> list[str]:
    valid = valid_city_names()
    cleaned = []
    for city in cities:
        normalized = normalize_city_name(city)
        if normalized in valid and normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


def default_cities() -> list[str]:
    cleaned = clean_city_list(DEFAULT_CITIES)
    return cleaned[:MAX_DISPLAY_CITIES] if len(cleaned) >= MAX_DISPLAY_CITIES else DEFAULT_CITIES.copy()

