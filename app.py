import streamlit as st
import requests
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA赛程查询", page_icon="篮球", layout="centered")
st.title("NBA赛事查询工具")

# 获取当前北京时间
beijing = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing)

# 转换为美东时间并获取日期字符串
eastern = pytz.timezone('America/New_York')
now_eastern = now_beijing.astimezone(eastern)
target_date = now_eastern.strftime('%Y-%m-%d')

# 获取篮彩日历数据
@st.cache_data(ttl=600)
def fetch Fixtures schedule():
    try:
        url = "https://zh-nbamatchinfo.com/api/schedule"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

with st spinner("正在加载NBA赛程数据..."):
    schedule = fetch Fixtures schedule()

if not schedule:
    st.stop()

# 查找目标日期的比赛
games = []
for game in schedule['games']:
    if game['gameDate'] == target_date:
        games.append(game)

# 显示结果
if not games:
    st.warning(f"北京时间 {now_beijing.strftime('%Y-%m-%d %H:%M')} 没有NBA比赛安排")
else:
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
