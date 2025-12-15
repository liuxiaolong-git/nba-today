import streamlit as st
import requests
import pytz
from datetime import datetime

st.set_page_config(page_title="NBA 赛程", page_icon="🏀", layout="centered")
st.title("🏀 NBA 今日赛程")
st.caption("数据来源: nba.com | 支持未来赛程")

# 获取北京时间今天（2025-12-15）
beijing = pytz.timezone('Asia/Shanghai')
today = datetime.now(beijing).strftime('%Y-%m-%d')

@st.cache_data(ttl=600)  # 缓存10分钟
def fetch_nba_schedule():
    try:
        url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ 无法加载赛程: {e}")
        return None

with st.spinner("正在加载 NBA 官方赛程..."):
    schedule = fetch_nba_schedule()

if not schedule:
    st.stop()

# 查找今天的比赛
games_today = []
for day in schedule['leagueSchedule']['gameDates']:
    if day['gameDate'] == today:
        games_today = day['games']
        break

# 显示结果
if not games_today:
    st.info(f"📅 北京时间 {today} 没有安排 NBA 比赛")
else:
    st.success(f"✅ 找到 {len(games_today)} 场比赛")
    for game in games_today:
        home = game['homeTeam']['teamName']
        away = game['awayTeam']['teamName']
        st.markdown(f"### 🕒 {away} @ {home}")
        st.divider()

st.caption("💡 数据每10分钟更新 | 来源: NBA 官方 CDN")
