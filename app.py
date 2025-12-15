import streamlit as st
import requests
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA 赛程", page_icon="🏀", layout="centered")
st.title("🏀 NBA 今日赛程（官方数据）")
st.caption("数据来源: nba.com | 支持未来赛程")

# 获取北京时间今天
beijing = pytz.timezone('Asia/Shanghai')
today_beijing = datetime.now(beijing).date()
today_str = today_beijing.strftime('%Y-%m-%d')

@st.cache_data(ttl=300)  # 缓存5分钟
def fetch_full_schedule():
    try:
        url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"❌ 无法加载赛程: {e}")
        return None

with st.spinner("正在加载完整赛程..."):
    schedule = fetch_full_schedule()

if not schedule:
    st.stop()

# 查找今天的比赛
games_today = []
for game_day in schedule['leagueSchedule']['gameDates']:
    if game_day['gameDate'] == today_str:
        games_today = game_day['games']
        break

# 显示结果
if not games_today:
    st.warning(f"📅 北京时间 {today_str} 没有安排 NBA 比赛")
else:
    st.success(f"✅ 找到 {len(games_today)} 场比赛")
    for g in games_today:
        home = g['homeTeam']['teamName']
        visitor = g['awayTeam']['teamName']
        status = g['gameStatus']
        
        # 状态处理
        if status == 1:
            icon, score = "🕒", f"{visitor} vs {home}"
        elif status == 2 or status == 3:
            h_score = g['homeTeam']['score']
            v_score = g['awayTeam']['score']
            icon, score = ("🔴", f"{visitor} **{v_score} - {h_score}** {home}") if status == 2 else ("✅", f"{visitor} **{v_score} - {h_score}** {home}")
        else:
            icon, score = "🕒", f"{visitor} vs {home}"

        st.markdown(f"### {icon} {score}")
        st.divider()

st.caption("💡 数据每5分钟更新 | 支持查看未来赛程")
