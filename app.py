import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程")

# 初始化会话状态
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)
today_str = now_beijing.strftime('%Y-%m-%d')

# 球队名称翻译字典（只保留队名）
team_translation = {
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
    """翻译球队名称（只保留队名）"""
    return team_translation.get(team_name_en, team_name_en)

@st.cache_data(ttl=30)
def fetch_nba_schedule(date_str):
    """获取NBA赛程数据"""
    try:
        eastern_tz = pytz.timezone('America/New_York')
        beijing_date = datetime.strptime(date_str, '%Y-%m-%d')
        beijing_date = beijing_tz.localize(beijing_date)
        eastern_date = beijing_date.astimezone(eastern_tz)

        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        params = {
            'dates': eastern_date.strftime('%Y%m%d'),
            'lang': 'zh',
            'region': 'cn'
        }

        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, params=params, headers=headers, timeout=8)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        st.error(f"获取赛程失败: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_player_stats(event_id):
    """获取球员统计数据"""
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        params = {'event': event_id}
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=8)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

def format_time(time_str):
    """格式化时间显示"""
    if not time_str or time_str == '0':
        return '0:00'
    time_str = str(time_str)
    if ':' in time_str:
        return time_str
    try:
        minutes = int(float(time_str))
        return f"{minutes}:00"
    except:
        return time_str

def parse_player_stats(game_data):
    """解析球员统计数据（使用正确的ESPN stats索引）"""
    try:
        boxscore = game_data.get('boxscore', {})
        players = boxscore.get('players', [])
        
        if len(players) < 2:
            return [], []
        
        # ESPN: players[0] = 主队(home), players[1] = 客队(away)
        home_team_players = players[0].get('statistics', [{}])[0].get('athletes', [])
        away_team_players = players[1].get('statistics', [{}])[0].get('athletes', [])
        
        def extract_player_info(player):
            athlete = player.get('athlete', {})
            stats = player.get('stats', [])
            # 至少需要14项基础统计
            if not athlete or len(stats) < 14:
                return None
            
            name = athlete.get('displayName', '')
            # 正确索引（参考ESPN实际返回）
            time_played = format_time(stats[0])   # MIN
            points      = str(stats[1])           # PTS
            rebounds    = str(stats[2])           # REB
            assists     = str(stats[3])           # AST
            turnovers   = str(stats[6])           # TO
            fgm         = str(stats[8])           # FGM
            fga         = str(stats[9])           # FGA
            three_pm    = str(stats[10])          # 3PM
            three_pa    = str(stats[11])          # 3PA
            
            return {
                '球员': name,
                '出场时间': time_played,
                '得分': points,
                '投篮': f"{fgm}/{fga}",
                '三分': f"{three_pm}/{three_pa}",
                '助攻': assists,
                '篮板': rebounds,
                '失误': turnovers
            }
        
        home_players_data = []
        away_players_data = []
        
        for p in home_team_players:
            info = extract_player_info(p)
            if info:
                home_players_data.append(info)
                
        for p in away_team_players:
            info = extract_player_info(p)
            if info:
                away_players_data.append(info)
                
        return away_players_data, home_players_data
        
    except Exception as e:
        if 'debug_info' not in st.session_state:
            st.session_state.debug_info = []
        error_info = f"解析球员数据错误: {str(e)}"
        st.session_state.debug_info.append(error_info)
        return [], []

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 查询设置")
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3)
    )

# 主界面
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

# 获取赛程数据
with st.spinner("正在加载赛程数据..."):
    schedule_data = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule_data or 'events' not in schedule_data:
    st.error("无法获取赛程数据，请稍后重试。")
    st.stop()

events = schedule_data.get('events', [])

if not events:
    st.info("今日暂无NBA比赛安排")
    st.stop()

# 显示比赛列表
for i, event in enumerate(events):
    event_id = event.get('id', '')
    status = event.get('status', {})
    status_detail = status.get('type', {}).get('state', 'pre')
    status_desc = status.get('type', {}).get('description', '未开始')

    if status_detail == 'in':
        status_badge = "🟢 进行中"
    elif status_detail == 'post':
        status_badge = "⚫ 已结束"
    else:
        status_badge = "⏳ 未开始"

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

    competitions = event.get('competitions', [])
    if not competitions:
        continue
    competition = competitions[0]
    competitors = competition.get('competitors', [])

    if len(competitors) < 2:
        continue

    # 注意：ESPN 中 competitors[0] 是客队，[1] 是主队
    away_team = competitors[0].get('team', {})
    home_team = competitors[1].get('team', {})

    away_name_cn = translate_team_name(away_team.get('displayName', '客队'))
    home_name_cn = translate_team_name(home_team.get('displayName', '主队'))

    away_score = competitors[0].get('score', '0')
    home_score = competitors[1].get('score', '0')

    with st.container():
        score_col1, score_col2, score_col3, score_col4, score_col5 = st.columns([2, 1, 0.5, 1, 2])
        with score_col1:
            st.markdown(f"**{away_name_cn}**")
        with score_col2:
            st.markdown(f"**{away_score}**")
        with score_col3:
            st.markdown("**VS**")
        with score_col4:
            st.markdown(f"**{home_score}**")
        with score_col5:
            st.markdown(f"**{home_name_cn}**")

        st.caption(f"{status_badge} | {status_desc} | ⏰ {game_time}")

        if status_detail in ['in', 'post']:
            with st.spinner("正在获取球员数据..."):
                game_data = fetch_player_stats(event_id)
                if game_data:
                    away_players, home_players = parse_player_stats(game_data)
                    
                    if away_players or home_players:
                        st.subheader("📊 球员数据")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**{away_name_cn}**")
                            if away_players:
                                df = pd.DataFrame(away_players)
                                df['得分_int'] = pd.to_numeric(df['得分'], errors='coerce')
                                df = df.sort_values('得分_int', ascending=False).drop('得分_int', axis=1)
                                st.dataframe(df, hide_index=True, use_container_width=True,
                                            height=min(300, len(away_players) * 35 + 38))
                            else:
                                st.info("暂无球员数据")
                                
                        with col2:
                            st.markdown(f"**{home_name_cn}**")
                            if home_players:
                                df = pd.DataFrame(home_players)
                                df['得分_int'] = pd.to_numeric(df['得分'], errors='coerce')
                                df = df.sort_values('得分_int', ascending=False).drop('得分_int', axis=1)
                                st.dataframe(df, hide_index=True, use_container_width=True,
                                            height=min(300, len(home_players) * 35 + 38))
                            else:
                                st.info("暂无球员数据")
                    else:
                        st.warning("暂无球员数据")
                        if 'debug_info' in st.session_state and st.session_state.debug_info:
                            with st.expander("查看调试信息"):
                                for info in st.session_state.debug_info:
                                    st.text(info)
                else:
                    st.warning("无法获取球员数据")

    if i < len(events) - 1:
        st.divider()

# 底部状态栏
st.divider()
col1, col2 = st.columns([2, 1])
with col1:
    st.caption(f"最后更新: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
with col2:
    if st.button("🔄 手动刷新"):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.rerun()
