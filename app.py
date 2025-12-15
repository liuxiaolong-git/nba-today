import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="centered")
st.title("🏀 NBA赛程速查")

# 初始化会话状态
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# 球队名称简写
team_abbr = {
    "Atlanta Hawks": "老鹰",
    "Boston Celtics": "凯尔特人", 
    "Brooklyn Nets": "篮网",
    "Charlotte Hornets": "黄蜂",
    "Chicago Bulls": "公牛",
    "Cleveland Cavaliers": "骑士",
    "Dallas Mavericks": "独行侠",
    "Denver Nuggets": "掘金",
    "Detroit Pistons": "活塞",
    "Golden State Warriors": "勇士",
    "Houston Rockets": "火箭",
    "Indiana Pacers": "步行者",
    "LA Clippers": "快船",
    "Los Angeles Clippers": "快船",
    "Los Angeles Lakers": "湖人",
    "Memphis Grizzlies": "灰熊",
    "Miami Heat": "热火",
    "Milwaukee Bucks": "雄鹿",
    "Minnesota Timberwolves": "森林狼",
    "New Orleans Pelicans": "鹈鹕",
    "New York Knicks": "尼克斯",
    "Oklahoma City Thunder": "雷霆",
    "Orlando Magic": "魔术",
    "Philadelphia 76ers": "76人",
    "Phoenix Suns": "太阳",
    "Portland Trail Blazers": "开拓者",
    "Sacramento Kings": "国王",
    "San Antonio Spurs": "马刺",
    "Toronto Raptors": "猛龙",
    "Utah Jazz": "爵士",
    "Washington Wizards": "奇才"
}

def translate_team_name(team_name_en):
    """翻译球队名称为简写"""
    return team_abbr.get(team_name_en, team_name_en[:4])

@st.cache_data(ttl=60, show_spinner=False)
def fetch_nba_schedule_fast(date_str):
    """快速获取NBA赛程数据 - 简化版"""
    try:
        url = "https://cdn.espn.com/core/nba/schedule"
        params = {
            'dates': date_str.replace('-', ''),
            'xhr': '1',
            'render': 'false',
            'device': 'desktop'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.espn.com/nba/schedule/_/date/'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_fallback_schedule():
    """备用方案：如果API失败，显示样例数据"""
    today = datetime.now().date()
    return {
        'content': {
            'schedule': [
                {
                    'date': today.strftime('%Y%m%d'),
                    'games': []
                }
            ]
        }
    }

# 日期选择
col1, col2 = st.columns([3, 1])
with col1:
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3),
        label_visibility="collapsed"
    )

with col2:
    if st.button("🔄", help="刷新数据"):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.rerun()

# 显示日期标题
st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')}")

# 快速获取赛程数据
schedule_data = fetch_nba_schedule_fast(selected_date.strftime('%Y-%m-%d'))

if not schedule_data:
    schedule_data = get_fallback_schedule()

# 解析赛程数据
try:
    games = []
    if 'content' in schedule_data and 'schedule' in schedule_data['content']:
        for day_schedule in schedule_data['content']['schedule']:
            if day_schedule['date'] == selected_date.strftime('%Y%m%d'):
                games = day_schedule.get('games', [])
                break
except:
    games = []

if not games:
    st.info("今日暂无NBA比赛安排")
    st.stop()

# 显示比赛列表
for game in games:
    # 提取比赛信息
    away_team = game.get('away', {})
    home_team = game.get('home', {})
    
    away_name = translate_team_name(away_team.get('displayName', '客队'))
    home_name = translate_team_name(home_team.get('displayName', '主队'))
    
    away_score = away_team.get('score', '')
    home_score = home_team.get('score', '')
    
    # 比赛状态
    status = game.get('status', {}).get('type', {}).get('state', 'pre')
    if status == 'in':
        status_text = "🟢 进行中"
    elif status == 'post':
        status_text = "⚫ 已结束"
    else:
        status_text = "⏳ 未开始"
    
    # 比赛时间
    game_time = game.get('time', '')
    if game_time:
        try:
            # 转换时间格式
            utc_time = datetime.strptime(game_time, '%Y-%m-%dT%H:%MZ')
            beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
            game_time_display = beijing_time.strftime("%H:%M")
        except:
            game_time_display = game_time
    else:
        game_time_display = "时间待定"
    
    # 显示比赛卡片
    with st.container():
        # 创建三列布局
        col_a, col_vs, col_h = st.columns([2, 1, 2])
        
        with col_a:
            st.markdown(f"**{away_name}**")
            if away_score:
                st.markdown(f"### {away_score}")
        
        with col_vs:
            st.markdown("**VS**")
            st.markdown(f"*{status_text}*")
            st.caption(game_time_display)
        
        with col_h:
            st.markdown(f"**{home_name}**", help_text="right")
            if home_score:
                st.markdown(f"### {home_score}", help_text="right")
    
    # 添加分隔线（最后一个比赛不加）
    if game != games[-1]:
        st.divider()

# 底部信息
st.caption(f"更新时间: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
