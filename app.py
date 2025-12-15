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

def parse_player_stats(game_data):
    """解析球员统计数据"""
    try:
        # 从boxscore中获取球员数据
        boxscore = game_data.get('boxscore', {})
        players = boxscore.get('players', [])
        
        if len(players) < 2:
            return [], []
        
        away_players_data = []
        home_players_data = []
        
        # 根据ESPN API，players[0]是主队，players[1]是客队
        home_team_players = players[0].get('statistics', [{}])[0].get('athletes', [])
        away_team_players = players[1].get('statistics', [{}])[0].get('athletes', [])
        
        # 处理主队球员
        for player in home_team_players:
            athlete = player.get('athlete', {})
            stats = player.get('stats', [])
            if athlete and stats:
                player_name = athlete.get('displayName', '')
                
                # 解析统计数据 - 正确的索引映射
                # ESPN API返回的stats数组顺序可能有所不同，我们需要正确解析
                # 通常顺序: 0=MIN, 1=FGM, 2=FGA, 3=FG3M, 4=FG3A, 5=FTM, 6=FTA, 7=REB, 8=AST, 9=STL, 10=BLK, 11=TO, 12=PF, 13=PTS
                # 但实际可能需要根据实际情况调整
                
                # 先获取所有stats值
                stats_values = [str(s) for s in stats]
                
                # 尝试不同的索引组合来找到正确的数据
                # 方法1: 查找得分(PTS) - 通常是最后一个或第一个
                points = '0'
                if len(stats) >= 14:
                    # 假设PTS在第13个位置
                    points = stats_values[13]
                elif len(stats) >= 2:
                    # 尝试第二个位置
                    points = stats_values[1]
                
                # 方法2: 查找出场时间(MIN) - 通常是第一个
                time_played = format_time(stats_values[0]) if stats_values else '0:00'
                
                # 方法3: 查找投篮数据 - 需要更复杂的逻辑
                fgm, fga, fg3m, fg3a, reb, ast, to = '0', '0', '0', '0', '0', '0', '0'
                
                # 尝试从原始数据中提取统计类别信息
                # 如果有categories信息，可以使用它
                if 'categories' in player:
                    categories = player.get('categories', [])
                    for category in categories:
                        category_name = category.get('name', '')
                        category_stats = category.get('stats', [])
                        if category_name == 'fieldGoals':
                            if len(category_stats) >= 2:
                                fgm = category_stats[0]
                                fga = category_stats[1]
                        elif category_name == 'threePointFieldGoals':
                            if len(category_stats) >= 2:
                                fg3m = category_stats[0]
                                fg3a = category_stats[1]
                        elif category_name == 'rebounds':
                            if len(category_stats) >= 1:
                                reb = category_stats[0]
                        elif category_name == 'assists':
                            if len(category_stats) >= 1:
                                ast = category_stats[0]
                        elif category_name == 'turnovers':
                            if len(category_stats) >= 1:
                                to = category_stats[0]
                
                # 如果通过categories没有找到数据，尝试基于常见的数据长度进行解析
                if fgm == '0' and fga == '0' and len(stats) >= 14:
                    # 尝试常见的数据格式
                    fgm = stats_values[1]  # FGM
                    fga = stats_values[2]  # FGA
                    fg3m = stats_values[3]  # FG3M
                    fg3a = stats_values[4]  # FG3A
                    reb = stats_values[7]  # REB
                    ast = stats_values[8]  # AST
                    to = stats_values[11]  # TO
                
                player_info = {
                    '球员': player_name,
                    '出场时间': time_played,
                    '得分': points,
                    '投篮': f"{fgm}/{fga}",
                    '三分': f"{fg3m}/{fg3a}",
                    '助攻': ast,
                    '篮板': reb,
                    '失误': to
                }
                home_players_data.append(player_info)
        
        # 处理客队球员
        for player in away_team_players:
            athlete = player.get('athlete', {})
            stats = player.get('stats', [])
            if athlete and stats:
                player_name = athlete.get('displayName', '')
                
                # 解析统计数据
                stats_values = [str(s) for s in stats]
                
                points = '0'
                if len(stats) >= 14:
                    points = stats_values[13]
                elif len(stats) >= 2:
                    points = stats_values[1]
                
                time_played = format_time(stats_values[0]) if stats_values else '0:00'
                
                fgm, fga, fg3m, fg3a, reb, ast, to = '0', '0', '0', '0', '0', '0', '0'
                
                if 'categories' in player:
                    categories = player.get('categories', [])
                    for category in categories:
                        category_name = category.get('name', '')
                        category_stats = category.get('stats', [])
                        if category_name == 'fieldGoals':
                            if len(category_stats) >= 2:
                                fgm = category_stats[0]
                                fga = category_stats[1]
                        elif category_name == 'threePointFieldGoals':
                            if len(category_stats) >= 2:
                                fg3m = category_stats[0]
                                fg3a = category_stats[1]
                        elif category_name == 'rebounds':
                            if len(category_stats) >= 1:
                                reb = category_stats[0]
                        elif category_name == 'assists':
                            if len(category_stats) >= 1:
                                ast = category_stats[0]
                        elif category_name == 'turnovers':
                            if len(category_stats) >= 1:
                                to = category_stats[0]
                
                if fgm == '0' and fga == '0' and len(stats) >= 14:
                    fgm = stats_values[1]
                    fga = stats_values[2]
                    fg3m = stats_values[3]
                    fg3a = stats_values[4]
                    reb = stats_values[7]
                    ast = stats_values[8]
                    to = stats_values[11]
                
                player_info = {
                    '球员': player_name,
                    '出场时间': time_played,
                    '得分': points,
                    '投篮': f"{fgm}/{fga}",
                    '三分': f"{fg3m}/{fg3a}",
                    '助攻': ast,
                    '篮板': reb,
                    '失误': to
                }
                away_players_data.append(player_info)
        
        return away_players_data, home_players_data
    except Exception as e:
        return [], []

def format_time(time_str):
    """格式化时间显示"""
    if not time_str:
        return '0:00'
    if ':' in str(time_str):
        return str(time_str)
    try:
        minutes = int(time_str)
        return f"{minutes}:00"
    except:
        return str(time_str)

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

    # 比赛状态
    if status_detail == 'in':
        status_badge = "🟢 进行中"
    elif status_detail == 'post':
        status_badge = "⚫ 已结束"
    else:
        status_badge = "⏳ 未开始"

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

            away_name_cn = translate_team_name(away_team.get('displayName', '客队'))
            home_name_cn = translate_team_name(home_team.get('displayName', '主队'))

            away_score = competitors[0].get('score', '0')
            home_score = competitors[1].get('score', '0')

            # 创建比赛卡片
            with st.container():
                # 比分卡片
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

                # 比赛信息
                st.caption(f"{status_badge} | {status_desc} | ⏰ {game_time}")

                # 显示球员数据（针对已结束或进行中的比赛）
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
                                        away_df = pd.DataFrame(away_players)
                                        # 按得分排序
                                        away_df['得分_int'] = pd.to_numeric(away_df['得分'], errors='coerce')
                                        away_df = away_df.sort_values('得分_int', ascending=False).drop('得分_int', axis=1)
                                        st.dataframe(
                                            away_df,
                                            hide_index=True,
                                            use_container_width=True,
                                            height=min(300, len(away_players) * 35 + 38)
                                        )
                                    else:
                                        st.info("暂无球员数据")
                                
                                with col2:
                                    st.markdown(f"**{home_name_cn}**")
                                    if home_players:
                                        home_df = pd.DataFrame(home_players)
                                        home_df['得分_int'] = pd.to_numeric(home_df['得分'], errors='coerce')
                                        home_df = home_df.sort_values('得分_int', ascending=False).drop('得分_int', axis=1)
                                        st.dataframe(
                                            home_df,
                                            hide_index=True,
                                            use_container_width=True,
                                            height=min(300, len(home_players) * 35 + 38)
                                        )
                                    else:
                                        st.info("暂无球员数据")
                            else:
                                st.warning("暂无球员数据")
                        else:
                            st.warning("无法获取球员数据")

    # 比赛之间的分隔线
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
