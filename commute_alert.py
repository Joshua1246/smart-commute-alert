import os
import requests

def get_commute_weather():
    # 1. 取得環境變數中的 Telegram 憑證 (資訊安全)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("[錯誤] 未設定 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID Secrets！")
        return

    # 桃園市地理座標 (24.9936, 121.3010)
    latitude = 24.9936
    longitude = 121.3010

    # 2. 呼叫 Open-Meteo API 取得天氣與 AQI 資料 (API 整合)
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=precipitation_probability,temperature_2m&forecast_days=1&timezone=Asia%2FTaipei"
    air_quality_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longitude}&hourly=us_aqi&forecast_days=1&timezone=Asia%2FTaipei"

    try:
        # 抓取天氣數據
        w_res = requests.get(weather_url, timeout=10)
        w_res.raise_for_status()
        w_data = w_res.json()

        # 抓取 AQI 數據
        aqi_res = requests.get(air_quality_url, timeout=10)
        aqi_res.raise_for_status()
        aqi_data = aqi_res.json()

        # 計算當日最高值
        max_pop = max([int(p) for p in w_data["hourly"]["precipitation_probability"] if p is not None])
        max_temp = max([float(t) for t in w_data["hourly"]["temperature_2m"] if t is not None])
        max_aqi = max([int(a) for a in aqi_data["hourly"]["us_aqi"] if a is not None])

        print(f"今日統計數據：最高降雨機率 {max_pop}% | 最高氣溫 {max_temp}°C | 最高 AQI {max_aqi}")

        # 3. 條件判斷邏輯 (可多個條件同時成立)
        advice_list = []

        if max_pop >= 60:
            advice_list.append("🌧️ 降雨機率達 60% 以上，出門請記得攜帶雨傘！")

        if max_temp >= 33:
            advice_list.append("☀️ 最高氣溫達 33°C 以上，請注意防曬並多補充水分！")

        if max_aqi >= 100:
            advice_list.append("😷 空氣品質 AQI 達 100 以上，建議配戴口罩出門！")

        # 6. 若所有條件皆正常時的訊息
        if not advice_list:
            advice_list.append("✨ 今日各項天氣指數皆正常，非常適合外出通勤！")

        # 組合完整的通知訊息 (Telegram 規格)
        message = (
            f"🚗【智慧通勤風險通知 - 桃園市】\n"
            f"─────────────────\n"
            f"📊 今日環境指標預報：\n"
            f"• 最高降雨機率：{max_pop}%\n"
            f"• 今日最高氣溫：{max_temp}°C\n"
            f"• 今日最高 AQI：{max_aqi}\n\n"
            f"💡 通勤建議：\n" + "\n".join(advice_list)
        )

        # 4. 發送至 Telegram Bot
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        
        response = requests.post(telegram_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("[成功] 通勤風險通知已順利發送至 Telegram！")
        else:
            print(f"[失敗] Telegram API 回應錯誤，HTTP 狀態碼：{response.status_code}，訊息：{response.text}")

    except requests.exceptions.RequestException as e:
        print(f"[錯誤] API 請求發生例外狀況：{e}")

if __name__ == "__main__":
    get_commute_weather()
