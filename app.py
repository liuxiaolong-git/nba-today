import streamlit as st
import requests
import pytz
from datetime import datetime
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA 赛程", page_icon="🏀", layout="centered")
st.title("🏀 NBA 今日赛程")
st.caption("数据来源: nba.com | 支持未来赛程")
st.set_page_config(page_title="NBA赛程查询", page_icon="篮球", layout="centered")
st.title("NBA赛事查询工具")

# 获取北京时间今天（2025-12-15）
# 获取当前北京时间
beijing = pytz.timezone('Asia/Shanghai')
today = datetime.now(beijing).strftime('%Y-%m-%d')
now_beijing = datetime.now(beijing)

@st.cache_data(ttl=600)  # 缓存10分钟
def fetch_nba_schedule():
# 转换为美东时间并获取日期字符串
eastern = pytz.timezone('America/New_York')
now_eastern = now_beijing.astimezone(eastern)
target_date = now_eastern.strftime('%Y-%m-%d')

# 获取篮彩日历数据
@st.cache_data(ttl=600)
def fetch Fixtures schedule():
    try:
        url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        url = "https://zh-nbamatchinfo.com/api/schedule"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ 无法加载赛程: {e}")
        st.error(f"数据加载失败: {e}")
        return None

with st.spinner("正在加载 NBA 官方赛程..."):
    schedule = fetch_nba_schedule()
with st spinner("正在加载NBA赛程数据..."):
    schedule = fetch Fixtures schedule()

if not schedule:
    st.stop()

# 查找今天的比赛
games_today = []
for day in schedule['leagueSchedule']['gameDates']:
    if day['gameDate'] == today:
        games_today = day['games']
        break
# 查找目标日期的比赛
games = []
for game in schedule['games']:
    if game['gameDate'] == target_date:
        games.append(game)

# 显示结果
if not games_today:
    st.info(f"📅 北京时间 {today} 没有安排 NBA 比赛")
if not games:
    st.warning(f"北京时间 {now_beijing.strftime('%Y-%m-%d %H:%M')} 没有NBA比赛安排")
else:
    st.success(f"✅ 找到 {len(games_today)} 场比赛")
    for game in games_today:
        home = game['homeTeam']['teamName']
        away = game['awayTeam']['teamName']
        st.markdown(f"### 🕒 {away} @ {home}")
        st.divider()

st.caption("💡 数据每10分钟更新 | 来源: NBA 官方 CDN")
    st.success(f"找到 {len(games)} 场比赛")
    for game in games:
        home = game['homeTeam']
        away = game['awayTeam']
        beijing_time = game['gameTimeBeijing']
        status = game['gameStatus']
        # 处理比赛状态
        if status == 'SCHEDULED':
            st markdown(f"### 🕒 {away} vs {home} | {beijing_time}")
        elif status == ' Final':
            h_score = game['homeTeamScore']
            v_score = game['awayTeamScore']
            st markdown(f"### ✅ {away} **{v_score} - {h_score}** {home} | {beijing_time}")
        else:
            st markdown(f"### ❓ {away} vs {home} | {beijing_time} (状态未知)")
        st divider()
