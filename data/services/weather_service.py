from __future__ import annotations

import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

from services.city_service import get_city_record

load_dotenv()

HOURS = [f"{hour:02d}" for hour in range(24)]
WEIGHTS = {"open_meteo": 4, "qweather": 3, "weatherapi": 3}
TIMEZONE = ZoneInfo("Asia/Shanghai")
DATE_OPTIONS = [
    ("今天", "06-23", "2026-06-23"),
    ("明天", "06-24", "2026-06-24"),
    ("后天", "06-25", "2026-06-25"),
]

MOCK_DEFAULT_DATA = {
    "上海市": ("阵雨", "09-11时", [60, 50, 46, 47, 53, 50, 45, 65, 77, 90, 87, 76, 78, 82, 75, 56, 69, 68, 67, 51, 52, 70, 70, 69]),
    "深圳市": ("雷阵雨", "12-14时", [17, 29, 29, 28, 28, 29, 29, 18, 13, 8, 10, 14, 18, 34, 37, 32, 18, 14, 11, 8, 4, 4, 4, 4]),
    "大连市": ("晴天", "00-03时", [5, 6, 8, 8, 8, 8, 8, 7, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4]),
    "天津市": ("多云", "17-19时", [3, 1, 1, 2, 2, 2, 2, 2, 1, 0, 1, 1, 1, 2, 21, 3, 4, 24, 4, 8, 23, 6, 12, 17]),
    "西安市": ("阴", "20-22时", [10, 10, 10, 10, 10, 10, 12, 10, 8, 3, 4, 4, 6, 9, 11, 12, 13, 17, 12, 12, 11, 31, 29, 29]),
    "无锡市": ("阵雨", "08-12时", [30, 31, 30, 30, 34, 42, 33, 31, 31, 60, 57, 60, 63, 64, 65, 64, 64, 64, 66, 67, 66, 63, 60, 58]),
    "长沙市": ("小阵雨", "00-03时", [46, 58, 62, 59, 74, 53, 77, 73, 64, 74, 67, 77, 70, 70, 64, 62, 59, 56, 56, 56, 55, 38, 37, 34]),
    "杭州市": ("小阵雨", "05-11时", [48, 71, 77, 62, 55, 71, 86, 85, 81, 82, 82, 81, 80, 70, 72, 78, 77, 75, 80, 73, 78, 77, 72, 73]),
    "成都市": ("小毛毛雨", "14-16时", [31, 27, 30, 17, 19, 26, 23, 25, 23, 8, 6, 24, 12, 40, 47, 50, 27, 23, 38, 34, 29, 10, 7, 10]),
    "宁波市": ("小阵雨", "00-07时", [76, 54, 84, 83, 80, 81, 81, 72, 69, 66, 54, 63, 63, 63, 70, 76, 78, 78, 76, 65, 70, 72, 74, 62]),
    "苏州市": ("阵雨", "10-15时", [31, 31, 33, 37, 44, 64, 63, 46, 50, 71, 72, 78, 74, 69, 70, 69, 69, 68, 68, 48, 48, 66, 66, 65]),
    "南京市": ("小毛毛雨", "20-22时", [32, 37, 42, 33, 40, 44, 35, 30, 27, 53, 40, 58, 59, 42, 62, 57, 40, 36, 33, 29, 44, 42, 40, 38]),
    "青岛市": ("晴天", "20-22时", [12, 13, 13, 13, 14, 13, 11, 1, 2, 3, 3, 2, 2, 3, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]),
    "沈阳市": ("阴", "20-22时", [3, 3, 4, 4, 6, 3, 3, 3, 3, 3, 4, 4, 4, 8, 8, 13, 14, 12, 12, 44, 42, 49, 59, 46]),
    "济南市": ("晴天", "00-03时", [3, 3, 5, 6, 7, 7, 7, 7, 6, 0, 0, 1, 1, 2, 3, 4, 3, 3, 2, 0, 0, 1, 2, 3]),
}


def _secret(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or os.getenv(name, "")).strip()


def safe_probability(value) -> int:
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, number))


def _selected_date(date_key: str) -> str:
    known = {item[2] for item in DATE_OPTIONS}
    if date_key in known:
        return date_key
    return DATE_OPTIONS[0][2]


def _weather_from_code(code) -> str:
    try:
        code = int(code)
    except (TypeError, ValueError):
        return "多云"
    if code in {0, 1}:
        return "晴天"
    if code in {2, 3, 45, 48}:
        return "多云"
    if code in {95, 96, 99}:
        return "雷阵雨"
    if code in {80, 81, 82}:
        return "阵雨"
    if code in {61, 63, 65, 66, 67}:
        return "小雨"
    if code in {51, 53, 55, 56, 57}:
        return "小毛毛雨"
    return "阴"


def _weather_from_peak(max_prob: int) -> str:
    if max_prob >= 80:
        return "强阵雨"
    if max_prob >= 60:
        return "阵雨"
    if max_prob >= 40:
        return "小阵雨"
    if max_prob >= 20:
        return "多云"
    return "晴天"


def _risk_window(hours: list[int]) -> str:
    if not hours:
        return "--"
    top_index = max(range(len(hours)), key=lambda index: hours[index])
    start = max(0, top_index - 1)
    end = min(23, top_index + 1)
    return f"{start:02d}-{end:02d}时"


def _mock_hours(city: str, date_key: str) -> tuple[str, list[int]]:
    if city in MOCK_DEFAULT_DATA:
        weather, _, hours = MOCK_DEFAULT_DATA[city]
        offset = {"2026-06-23": 0, "2026-06-24": -7, "2026-06-25": 5}.get(date_key, 0)
        return weather, [safe_probability(value + offset) for value in hours]

    seed = sum(ord(char) for char in f"{city}-{date_key}")
    base = seed % 38
    peak = (seed // 7) % 24
    values = []
    for hour in range(24):
        distance = min((hour - peak) % 24, (peak - hour) % 24)
        boost = max(0, 6 - distance) * (4 + seed % 6)
        wobble = ((seed + hour * 13) % 17) - 6
        values.append(safe_probability(base + boost + wobble))
    return _weather_from_peak(max(values)), values


def _open_meteo(record: dict, date_key: str) -> dict | None:
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": record["lat"],
            "longitude": record["lon"],
            "hourly": "precipitation_probability,weather_code",
            "forecast_days": 3,
            "timezone": "Asia/Shanghai",
        },
        timeout=8,
    )
    response.raise_for_status()
    hourly = response.json().get("hourly", {})
    times = hourly.get("time", [])
    probs = hourly.get("precipitation_probability", [])
    codes = hourly.get("weather_code", [])
    values = [None] * 24
    weather_codes = []
    for index, time_text in enumerate(times):
        if not str(time_text).startswith(date_key):
            continue
        hour = int(str(time_text)[11:13])
        values[hour] = safe_probability(probs[index] if index < len(probs) else 0)
        if index < len(codes):
            weather_codes.append(codes[index])
    if all(value is None for value in values):
        return None
    filled = [safe_probability(value) for value in values]
    weather = _weather_from_code(weather_codes[0]) if weather_codes else _weather_from_peak(max(filled))
    return {"source": "Open-Meteo 4.0", "weight": WEIGHTS["open_meteo"], "weather": weather, "hours": filled}


def _qweather(record: dict, date_key: str) -> dict | None:
    api_key = _secret("QWEATHER_API_KEY")
    host = _secret("QWEATHER_API_HOST")
    if not api_key or not host:
        return None
    url = f"https://{host}/v7/weather/24h"
    response = requests.get(url, params={"location": record["location_id"], "key": api_key}, timeout=8)
    response.raise_for_status()
    payload = response.json()
    if str(payload.get("code")) != "200":
        return None
    values = [None] * 24
    weather = ""
    for item in payload.get("hourly", []):
        fx_time = str(item.get("fxTime", ""))
        local_time = fx_time[:13]
        if not local_time.startswith(date_key):
            continue
        hour = int(local_time[11:13])
        values[hour] = safe_probability(item.get("pop", 0))
        weather = weather or str(item.get("text", ""))
    if all(value is None for value in values):
        return None
    filled = [safe_probability(value) for value in values]
    return {"source": "和风天气 3.0", "weight": WEIGHTS["qweather"], "weather": weather or _weather_from_peak(max(filled)), "hours": filled}


def _weatherapi(record: dict, date_key: str) -> dict | None:
    api_key = _secret("WEATHERAPI_KEY")
    if not api_key:
        return None
    response = requests.get(
        "https://api.weatherapi.com/v1/forecast.json",
        params={"key": api_key, "q": f"{record['lat']},{record['lon']}", "days": 3, "aqi": "no", "alerts": "no"},
        timeout=8,
    )
    response.raise_for_status()
    days = response.json().get("forecast", {}).get("forecastday", [])
    target = next((day for day in days if day.get("date") == date_key), None)
    if not target:
        return None
    values = [None] * 24
    weather = ""
    for item in target.get("hour", []):
        time_text = str(item.get("time", ""))
        if not time_text.startswith(date_key):
            continue
        hour = int(time_text[11:13])
        values[hour] = safe_probability(item.get("chance_of_rain", 0))
        condition = item.get("condition", {}) or {}
        weather = weather or str(condition.get("text", ""))
    if all(value is None for value in values):
        return None
    filled = [safe_probability(value) for value in values]
    return {"source": "WeatherAPI 3.0", "weight": WEIGHTS["weatherapi"], "weather": weather or _weather_from_peak(max(filled)), "hours": filled}


def _merge_sources(city: str, date_key: str, source_results: list[dict]) -> tuple[str, list[int], list[str]]:
    valid = [result for result in source_results if result and result.get("hours")]
    if not valid:
        weather, hours = _mock_hours(city, date_key)
        return weather, hours, ["本地兜底数据"]

    merged = []
    for index in range(24):
        total_weight = 0
        total_value = 0
        for result in valid:
            weight = int(result.get("weight", 0) or 0)
            total_weight += weight
            total_value += safe_probability(result["hours"][index]) * weight
        merged.append(safe_probability(total_value / total_weight if total_weight else 0))

    weather = next((result.get("weather") for result in valid if result.get("weather")), _weather_from_peak(max(merged)))
    sources = [result["source"] for result in valid if result.get("source")]
    return weather, merged, sources


def _build_city_row(city: str, date_key: str) -> tuple[dict | None, list[str]]:
    record = get_city_record(city)
    if not record:
        return None, [f"{city} 不在城市池中"]
    if not record.get("location_id") or pd.isna(record.get("lat")) or pd.isna(record.get("lon")):
        return None, [f"{city} 缺少定位信息，已跳过"]

    failures = []
    source_results = []
    for fetcher in (_open_meteo, _qweather, _weatherapi):
        try:
            source_results.append(fetcher(record, date_key))
        except Exception as exc:
            failures.append(f"{city} {fetcher.__name__.replace('_', '')} 请求失败，已降级")

    weather, hours, sources = _merge_sources(city, date_key, source_results)
    max_prob = max(hours) if hours else 0
    row = {
        "city": city,
        "province": record.get("province", ""),
        "weather": weather,
        "max_prob": max_prob,
        "risk_window": _risk_window(hours),
        "sources": "、".join(sources),
    }
    for index, hour in enumerate(HOURS):
        row[hour] = safe_probability(hours[index] if index < len(hours) else 0)
    return row, failures


@st.cache_data(ttl=60 * 60 * 3, show_spinner=False)
def get_weather_data(cities: tuple[str, ...], date_key: str, refresh_token: int = 0) -> tuple[pd.DataFrame, list[str], str]:
    target_date = _selected_date(date_key)
    rows = []
    messages = []
    for city in cities:
        row, failures = _build_city_row(city, target_date)
        messages.extend(failures)
        if row:
            rows.append(row)
    updated_at = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M")
    return pd.DataFrame(rows), messages, updated_at


def filter_by_risk(df: pd.DataFrame, risk_filter: str) -> pd.DataFrame:
    if df.empty or "max_prob" not in df:
        return df
    if risk_filter == "高风险":
        return df[df["max_prob"] >= 80]
    if risk_filter == "中高风险":
        return df[(df["max_prob"] >= 60) & (df["max_prob"] < 80)]
    if risk_filter == "中低风险":
        return df[(df["max_prob"] >= 30) & (df["max_prob"] < 60)]
    if risk_filter == "低风险":
        return df[df["max_prob"] < 30]
    return df


def summarize(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"top_city": "--", "top_prob": 0, "high_count": 0, "high_cities": "暂无", "peak_window": "--", "sources": "暂无"}
    safe = df.copy()
    safe["max_prob"] = pd.to_numeric(safe["max_prob"], errors="coerce").fillna(0).astype(int)
    top = safe.sort_values("max_prob", ascending=False).iloc[0]
    high = safe[safe["max_prob"] >= 80].sort_values("max_prob", ascending=False)
    hour_means = [(hour, pd.to_numeric(safe[hour], errors="coerce").fillna(0).mean()) for hour in HOURS if hour in safe]
    if hour_means:
        peak_hour = int(max(hour_means, key=lambda item: item[1])[0])
        peak_window = f"{max(0, peak_hour - 1):02d}:00 - {min(23, peak_hour + 1):02d}:00"
    else:
        peak_window = "--"
    sources = "、".join(dict.fromkeys("、".join(safe.get("sources", pd.Series(dtype=str)).dropna().astype(str)).split("、")))
    return {
        "top_city": str(top["city"]),
        "top_prob": int(top["max_prob"]),
        "high_count": int(len(high)),
        "high_cities": "、".join(high["city"].head(4).tolist()) or "暂无",
        "peak_window": peak_window,
        "sources": sources or "暂无",
    }

