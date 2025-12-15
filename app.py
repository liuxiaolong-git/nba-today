import streamlit as st
import requests
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="centered")
st.title("NBA今日赛程查询")
st.caption("数据来源: NBA官方CDN | 支持未来赛程")

# 获取北京时间今天
beijing = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing)

# 转换为美东时间并获取日期字符串
eastern = pytz.timezone('America/New_York')
now_eastern = now_beijing.astimezone(eastern)
target_date = now_eastern.strftime('%Y-%m-%d')

@st.cache_data(ttl=600)  # 缓存10分钟
def fetch_nba_schedule():
    """从NBA官方CDN获取完整赛程数据"""
    try:
        url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

with st spinner("正在加载NBA官方赛程数据..."):
    schedule = fetch_nba_schedule()

if not schedule:
    st.stop()

# 查找目标日期的比赛
games = []
for day in schedule['leagueSchedule']['gameDates']:
    if day['gameDate'] == target_date:
        games.extend(day['games'])
        break

# 如果没有找到当天的比赛，检查前一天是否有比赛在当天北京时间举行
if not games:
    previous_eastern_date = (now_eastern - timedelta(days=1)).strftime('%Y-%m-%d')
    for day in schedule['leagueSchedule']['gameDates']:
        if day['gameDate'] == previous_eastern_date:
            # 将前一天的ET时间转换为北京时间，检查是否在目标日期内
            for game in day['games']:
                et_time_str = game['gameTimeET']
                et_time = datetime.strptime(f"{previous_eastern_date} {et_time_str}", "%Y-%m-%d %I:%M %p")
                beijing_time = et_time.astimezone(beijing).strftime("%Y-%m-%d")
                if beijing_time == today:
                    games.append(game)
            break

# 显示结果
if not games:
    st.warning(f"北京时间 {now_beijing.strftime('%Y-%m-%d %H:%M')} 没有NBA比赛安排")
else:
    st.success(f"找到 {len(games)} 场比赛")
    for game in games:
        home = game['homeTeam']['teamName']
        away = game['awayTeam']['teamName']
        et_time = game['gameTimeET']
        status = game['gameStatus']
        # 转换比赛时间到北京时间
        game_time_eastern = datetime.strptime(f"{target_date} {et_time}", "%Y-%m-%d %I:%M %p")
        game_time_eastern = eastern.localize(game_time_eastern)
        game_time_beijing = game_time_eastern astimezone(beijing).strftime("%Y-%m-%d %H:%M")
        # 处理比赛状态
        if status == 1:
            status_text = "未开始"
            color = "green"
        elif status == 2:
            status_text = "进行中"
            color = "blue"
        elif status == 3:
            status_text = "结束"
            color = "red"
        else:
            status_text = "状态未知"
            color = "gray"
        # 显示比赛信息
        st markdown(f"### <span style='color:{color}'>**{status_text}**</span> | {away} vs {home}")
        st markdown(f"#### 北京时间: {game_time_beijing}")
        # 添加分隔线
        st divider()
