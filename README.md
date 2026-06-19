# 城市72小时降雨概率雷达

基于 Streamlit 的天气看板，融合 Open-Meteo、和风天气、WeatherAPI 三个来源，展示城市分小时综合降雨概率。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

本地开发可在项目根目录创建 `.env`：

```bash
QWEATHER_API_KEY=你的和风天气密钥
QWEATHER_API_HOST=你的和风天气API Host
WEATHERAPI_KEY=你的WeatherAPI密钥
```

## Streamlit Community Cloud 部署

部署时不要上传 `.env`。在 Streamlit Cloud 的 App secrets 中填写：

```toml
QWEATHER_API_KEY = "你的和风天气密钥"
QWEATHER_API_HOST = "你的和风天气API Host"
WEATHERAPI_KEY = "你的WeatherAPI密钥"
```

天气接口数据缓存 3 小时，同一云端实例内的访问者会共用缓存，减少 API 调用量。
