import requests
from statistics import mean
import time


# ==========================================
# 模块1：城市数据接口 (Data Interface)
# ==========================================

def get_provincial_capitals():
    """
    【静态接口】返回中国34个省级行政中心（省会/直辖市/首府）的坐标数据
    数据源：标准地理坐标
    """
    return [
        {"name": "北京", "lat": 39.90, "lon": 116.40},
        {"name": "上海", "lat": 31.23, "lon": 121.47},
        {"name": "天津", "lat": 39.08, "lon": 117.20},
        {"name": "重庆", "lat": 29.56, "lon": 106.55},
        {"name": "哈尔滨", "lat": 45.80, "lon": 126.53},
        {"name": "长春", "lat": 43.81, "lon": 125.32},
        {"name": "沈阳", "lat": 41.80, "lon": 123.43},
        {"name": "呼和浩特", "lat": 40.84, "lon": 111.75},
        {"name": "石家庄", "lat": 38.04, "lon": 114.51},
        {"name": "太原", "lat": 37.87, "lon": 112.55},
        {"name": "济南", "lat": 36.65, "lon": 117.12},
        {"name": "郑州", "lat": 34.75, "lon": 113.62},
        {"name": "西安", "lat": 34.34, "lon": 108.94},
        {"name": "兰州", "lat": 36.06, "lon": 103.83},
        {"name": "银川", "lat": 38.48, "lon": 106.23},
        {"name": "西宁", "lat": 36.62, "lon": 101.78},
        {"name": "乌鲁木齐", "lat": 43.82, "lon": 87.62},
        {"name": "合肥", "lat": 31.82, "lon": 117.23},
        {"name": "南京", "lat": 32.06, "lon": 118.80},
        {"name": "杭州", "lat": 30.27, "lon": 120.15},
        {"name": "福州", "lat": 26.07, "lon": 119.30},
        {"name": "南昌", "lat": 28.68, "lon": 115.85},
        {"name": "武汉", "lat": 30.59, "lon": 114.30},
        {"name": "长沙", "lat": 28.23, "lon": 112.93},
        {"name": "广州", "lat": 23.13, "lon": 113.26},
        {"name": "南宁", "lat": 22.82, "lon": 108.37},
        {"name": "海口", "lat": 20.04, "lon": 110.33},
        {"name": "成都", "lat": 30.57, "lon": 104.06},
        {"name": "贵阳", "lat": 26.65, "lon": 106.63},
        {"name": "昆明", "lat": 25.04, "lon": 102.71},
        {"name": "拉萨", "lat": 29.65, "lon": 91.11},
        {"name": "台北", "lat": 25.03, "lon": 121.50},
        {"name": "香港", "lat": 22.32, "lon": 114.17},
        {"name": "澳门", "lat": 22.19, "lon": 113.54}
    ]


def search_city_coordinates(city_name):
    """
    【动态接口】使用 Open-Meteo Geocoding API 搜索任意城市坐标
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "zh",  # 尝试返回中文名
        "format": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if "results" in data:
            result = data["results"][0]
            return {
                "name": city_name,  # 使用用户输入的名称
                "lat": result["latitude"],
                "lon": result["longitude"]
            }
        else:
            return None
    except Exception as e:
        print(f"搜索城市失败: {e}")
        return None


# ==========================================
# 模块2：天气与入冬判断逻辑
# ==========================================

def get_recent_temps(lat, lon):
    """获取过去5天的气温数据"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "timezone": "Asia/Shanghai",
        "past_days": 5,
        "forecast_days": 1
    }
    try:
        # 增加一个微小的延时，防止请求过快
        time.sleep(0.1)
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        daily = data.get("daily", {})
        max_t = daily.get("temperature_2m_max", [])
        min_t = daily.get("temperature_2m_min", [])

        # 取前5天计算平均
        means = []
        if len(max_t) >= 5:
            for i in range(5):
                means.append((max_t[i] + min_t[i]) / 2)
        return means
    except:
        return []


def judge_winter(daily_means):
    """判断逻辑：连续5天滑动平均 < 10度"""
    if not daily_means: return "数据错误", 0

    avg = mean(daily_means)
    if avg < 10:
        return "❄️ 已入冬", avg
    elif avg < 15:
        return "🍂 深秋", avg
    elif avg < 22:
        return "🍁 秋季", avg
    else:
        return "🌞 温暖", avg


# ==========================================
# 主程序
# ==========================================

def main():
    print("正在初始化全国城市数据...\n")

    # 1. 获取内置的全国主要城市列表
    cities = get_provincial_capitals()

    # 2. (可选) 你可以在这里添加你想查询的其他特定城市
    # print("正在搜索额外城市: 大理...")
    # extra_city = search_city_coordinates("Dali") # 建议用拼音搜索更准
    # if extra_city: cities.append(extra_city)

    print(f"{'城市':<6} | {'状态':<8} | {'5日均温':<8} | {'进度条'}")
    print("-" * 50)

    # 3. 循环获取天气并判断
    # 按照温度从低到高排序，更有观感
    results = []

    total = len(cities)
    for i, city in enumerate(cities):
        # 简单的进度提示
        print(f"\r正在获取数据 ({i + 1}/{total}): {city['name']}...", end="", flush=True)

        means = get_recent_temps(city['lat'], city['lon'])
        status, avg_temp = judge_winter(means)

        results.append({
            "city": city['name'],
            "status": status,
            "temp": avg_temp
        })

    print("\n" + "=" * 50)

    # 4. 排序：按温度从冷到热
    results.sort(key=lambda x: x['temp'])

    for r in results:
        # 简单的可视化进度条
        bar_len = int(r['temp']) if r['temp'] > 0 else 0
        bar = "█" * bar_len

        print(f"{r['city']:<6} | {r['status']:<8} | {r['temp']:>5.1f}℃ | {bar}")


if __name__ == "__main__":
    main()