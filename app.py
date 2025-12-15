import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="centered")
st.title("🏀 NBA赛程速查")

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
        st.rerun()

# 显示日期标题
st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')}")

# 快速获取赛程数据
@st.cache_data(ttl=60, show_spinner=False)
def get_nba_games(date_str):
    """获取NBA比赛数据"""
    try:
        # 使用更稳定的API
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        date_formatted = date_str.replace('-', '')
        params = {'dates': date_formatted}
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                try:
                    # 比赛状态
                    status = event.get('status', {})
                    status_type = status.get('type', {}).get('state', 'pre')
                    
                    # 比赛时间
                    date_str = event.get('date', '')
                    if date_str:
                        try:
                            utc_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            beijing_time = utc_time.astimezone(beijing_tz)
                            game_time = beijing_time.strftime("%H:%M")
                        except:
                            game_time = "时间待定"
                    else:
                        game_time = "时间待定"
                    
                    # 参赛队伍
                    competitions = event.get('competitions', [])
                    if competitions:
                        competition = competitions[0]
                        competitors = competition.get('competitors', [])
                        
                        if len(competitors) >= 2:
                            away_team = competitors[0].get('team', {})
                            home_team = competitors[1].get('team', {})
                            
                            away_name = translate_team_name(away_team.get('displayName', '客队'))
                            home_name = translate_team_name(home_team.get('displayName', '主队'))
                            
                            away_score = competitors[0].get('score', '')
                            home_score = competitors[1].get('score', '')
                            
                            games.append({
                                'away_name': away_name,
                                'home_name': home_name,
                                'away_score': away_score,
                                'home_score': home_score,
                                'status': status_type,
                                'game_time': game_time,
                                'status_desc': status.get('type', {}).get('description', '未开始')
                            })
                except:
                    continue
            
            return games
    except Exception as e:
        st.error(f"获取数据失败: {str(e)[:50]}")
    
    return []

# 获取并显示比赛
games = get_nba_games(selected_date.strftime('%Y-%m-%d'))

if not games:
    st.info("今日暂无NBA比赛安排")
    st.stop()

# 显示比赛列表
for i, game in enumerate(games):
    # 比赛状态
    status = game['status']
    if status == 'in':
        status_text = "🟢 进行中"
    elif status == 'post':
        status_text = "⚫ 已结束"
    else:
        status_text = "⏳ 未开始"
    
    # 创建三列布局
    col_a, col_vs, col_h = st.columns([2, 1, 2])
    
    with col_a:
        st.markdown(f"**{game['away_name']}**")
        if game['away_score']:
            st.markdown(f"### {game['away_score']}")
    
    with col_vs:
        st.markdown("**VS**")
        st.markdown(f"*{status_text}*")
        st.caption(game['game_time'])
    
    with col_h:
        st.markdown(f"**{game['home_name']}**")
        if game['home_score']:
            st.markdown(f"### {game['home_score']}")
    
    # 比赛状态描述
    if game['status_desc'] != '未开始':
        st.caption(f"状态: {game['status_desc']}")
    
    # 添加分隔线（最后一个比赛不加）
    if i < len(games) - 1:
        st.divider()

# 底部信息
st.caption(f"更新时间: {datetime.now(beijing_tz).strftime('%H:%M:%S')} | 共 {len(games)} 场比赛")
