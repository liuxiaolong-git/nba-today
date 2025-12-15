import streamlit as st
import requests
import pytz
from datetime import datetime

# 页面配置：适配手机 + 添加图标
st.set_page_config(
    page_title="NBA 今日赛程",
    page_icon="🏀",
    layout="centered"
)

# 标题和说明
st.title("🏀 NBA 今日赛程")
st.caption("数据来源: balldontlie.io | 美东时间")

# 获取美东时间“今天”
eastern = pytz.timezone('US/Eastern')
today = datetime.now(eastern).strftime('%Y-%m-%d')

# 带缓存的数据获取函数（60秒刷新一次）
@st.cache_data(ttl=60)
def fetch_games(date):
    try:
        url = "https://www.balldontlie.io/api/v1/games"
        params = {'dates[]': date, 'per_page': 100}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        st.error(f"❌ 获取数据失败: {e}")
        return []

# 加载比赛
games = fetch_games(today)

# 显示内容
if not games:
    st.info(f"📅 {today}（美东时间）没有 NBA 比赛。")
else:
    for game in games:
        home_team = game['home_team']['full_name']
        visitor_team = game['visitor_team']['full_name']
        home_score = game['home_team_score']
        visitor_score = game['visitor_team_score']
        status = game['status']

        # 状态图标
        if "Final" in status:
            icon = "✅"
        elif "Quarter" in status or "Half" in status:
            icon = "🔴"
        else:
            icon = "🕒"

        # 构建比分文本
        if home_score == 0 and visitor_score == 0 and "Scheduled" in status:
            score_line = f"{visitor_team} vs {home_team}"
        else:
            score_line = f"{visitor_team} **{visitor_score} - {home_score}** {home_team}"

        # 显示比赛卡片
        st.markdown(f"### {icon} {score_line}")
        st.caption(status)
        st.divider()

# 底部提示
st.caption("💡 下拉页面即可刷新最新数据")