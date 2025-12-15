import streamlit as st
import requests
import pandas as pd
import pytz
import time
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程")
st.caption("数据来源: ESPN公开接口 | 全中文 | 自动刷新")

# 初始化会话状态
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'expanded_games' not in st.session_state:
    st.session_state.expanded_games = {}
if 'player_data_cache' not in st.session_state:
    st.session_state.player_data_cache = {}

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)
today_str = now_beijing.strftime('%Y-%m-%d')

# NBA球队中英文对照表（去掉地名，只保留队名）
NBA_TEAMS_CN = {
    "Atlanta Hawks": "老鹰", "Boston Celtics": "凯尔特人",
    "Brooklyn Nets": "篮网", "Charlotte Hornets": "黄蜂",
    "Chicago Bulls": "公牛", "Cleveland Cavaliers": "骑士",
    "Detroit Pistons": "活塞", "Indiana Pacers": "步行者",
    "Miami Heat": "热火", "Milwaukee Bucks": "雄鹿",
    "New York Knicks": "尼克斯", "Orlando Magic": "魔术",
    "Philadelphia 76ers": "76人", "Toronto Raptors": "猛龙",
    "Washington Wizards": "奇才", "Dallas Mavericks": "独行侠",
    "Denver Nuggets": "掘金", "Golden State Warriors": "勇士",
    "Houston Rockets": "火箭", "LA Clippers": "快船",
    "Los Angeles Lakers": "湖人", "Memphis Grizzlies": "灰熊",
    "Minnesota Timberwolves": "森林狼", "New Orleans Pelicans": "鹈鹕",
    "Oklahoma City Thunder": "雷霆", "Phoenix Suns": "太阳",
    "Portland Trail Blazers": "开拓者", "Sacramento Kings": "国王",
    "San Antonio Spurs": "马刺", "Utah Jazz": "爵士"
}

# NBA球员中英文对照表
NBA_PLAYERS_CN = {
    "LeBron James": "詹姆斯", "Anthony Davis": "戴维斯",
    "Stephen Curry": "库里", "Klay Thompson": "汤普森",
    "Kevin Durant": "杜兰特", "James Harden": "哈登",
    "Giannis Antetokounmpo": "字母哥", "Luka Doncic": "东契奇",
    "Nikola Jokic": "约基奇", "Joel Embiid": "恩比德",
    "Jayson Tatum": "塔图姆", "Damian Lillard": "利拉德",
    "Kawhi Leonard": "伦纳德", "Paul George": "乔治",
    "Donovan Mitchell": "米切尔", "Trae Young": "特雷杨",
    "Zion Williamson": "威廉森", "Ja Morant": "莫兰特",
    "Devin Booker": "布克", "Chris Paul": "保罗",
    "Kyrie Irving": "欧文", "Russell Westbrook": "威少",
    "Anthony Edwards": "爱德华兹", "Jalen Brunson": "布伦森",
    
    # 示例中的球员
    "Darius Garland": "加兰", "Jaylon Tyson": "泰森",
    "Dean Wade": "韦德", "Thomas Bryant": "布莱恩特",
    "Jarrett Allen": "阿伦", "Lonzo Ball": "鲍尔",
    "Nae'Qwan Tomlin": "汤姆林", "De'Andre Hunter": "亨特",
    "Craig Porter": "波特"
}

def translate_player_name(english_name):
    """将英文球员名转换为中文"""
    if english_name in NBA_PLAYERS_CN:
        return NBA_PLAYERS_CN[english_name]
    elif "Jr." in english_name:
        return english_name.replace("Jr.", "小")
    elif "III" in english_name:
        return english_name.replace(" III", "三世")
    elif "II" in english_name:
        return english_name.replace(" II", "二世")
    return english_name

def translate_team_name(english_name):
    """将英文队名转换为中文"""
    return NBA_TEAMS_CN.get(english_name, english_name)

@st.cache_data(ttl=10)
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
        return None

def fetch_game_details(game_id):
    """获取比赛详细数据，包括球员统计"""
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        params = {'event': game_id}
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=8)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        return None

def parse_player_stats_detailed(game_details, team_id):
    """详细球员数据解析函数 - 修复数据为0的问题"""
    players_data = []
    
    if not game_details:
        return players_data
    
    # 尝试多种方法解析球员数据
    # 方法1：从boxscore -> players获取
    boxscore = game_details.get('boxscore', {})
    players = boxscore.get('players', [])
    
    for team_players in players:
        if str(team_players.get('team', {}).get('id')) == str(team_id):
            # 初始化球员数据字典
            player_stats_dict = {}
            
            # 先收集所有球员的基本信息
            for stat_category in team_players.get('statistics', []):
                athletes = stat_category.get('athletes', [])
                
                for athlete_info in athletes:
                    player = athlete_info.get('athlete', {})
                    if player:
                        player_id = player.get('id', '')
                        player_name = player.get('displayName', '')
                        
                        if player_id not in player_stats_dict:
                            player_stats_dict[player_id] = {
                                '球员': translate_player_name(player_name),
                                '出场时间': '0:00',
                                '得分': '0',
                                '投篮': '0-0',
                                '三分': '0-0',
                                '助攻': '0',
                                '篮板': '0',
                                '失误': '0'
                            }
            
            # 然后填充具体统计数据
            for stat_category in team_players.get('statistics', []):
                category_name = stat_category.get('name', '')
                athletes = stat_category.get('athletes', [])
                
                for athlete_info in athletes:
                    player = athlete_info.get('athlete', {})
                    stats = athlete_info.get('stats', [])
                    
                    if player and stats:
                        player_id = player.get('id', '')
                        if player_id in player_stats_dict:
                            if category_name == 'minutes':
                                # 出场时间
                                if len(stats) > 0 and stats[0]:
                                    player_stats_dict[player_id]['出场时间'] = format_minutes(stats[0])
                            elif category_name == 'points':
                                # 得分
                                if len(stats) > 0 and stats[0]:
                                    player_stats_dict[player_id]['得分'] = str(stats[0])
                            elif category_name == 'assists':
                                # 助攻
                                if len(stats) > 0 and stats[0]:
                                    player_stats_dict[player_id]['助攻'] = str(stats[0])
                            elif category_name == 'rebounds':
                                # 篮板
                                if len(stats) > 0 and stats[0]:
                                    player_stats_dict[player_id]['篮板'] = str(stats[0])
                            elif category_name == 'turnovers':
                                # 失误
                                if len(stats) > 0 and stats[0]:
                                    player_stats_dict[player_id]['失误'] = str(stats[0])
                            elif category_name == 'fieldGoals':
                                # 投篮
                                if len(stats) > 1 and stats[0] is not None and stats[1] is not None:
                                    made = int(stats[0]) if stats[0] is not None else 0
                                    attempted = int(stats[1]) if stats[1] is not None else 0
                                    player_stats_dict[player_id]['投篮'] = f"{made}-{attempted}"
                            elif category_name == 'threePointFieldGoals':
                                # 三分
                                if len(stats) > 1 and stats[0] is not None and stats[1] is not None:
                                    made = int(stats[0]) if stats[0] is not None else 0
                                    attempted = int(stats[1]) if stats[1] is not None else 0
                                    player_stats_dict[player_id]['三分'] = f"{made}-{attempted}"
            
            # 将字典转换为列表
            players_data = list(player_stats_dict.values())
            break
    
    # 方法2：如果上面没获取到，尝试从其他位置获取
    if not players_data:
        # 尝试从header -> competitions -> competitors获取
        header = game_details.get('header', {})
        competitions = header.get('competitions', [])
        
        for competition in competitions:
            competitors = competition.get('competitors', [])
            
            for competitor in competitors:
                if str(competitor.get('team', {}).get('id')) == str(team_id):
                    # 获取球员名单
                    athletes = competitor.get('athletes', [])
                    
                    for athlete in athletes:
                        player = athlete.get('athlete', {})
                        if player:
                            player_name = player.get('displayName', '')
                            stats = athlete.get('stats', [])
                            
                            player_data = {
                                '球员': translate_player_name(player_name),
                                '出场时间': '0:00',
                                '得分': '0',
                                '投篮': '0-0',
                                '三分': '0-0',
                                '助攻': '0',
                                '篮板': '0',
                                '失误': '0'
                            }
                            
                            # 解析统计数据
                            if stats:
                                for stat in stats:
                                    stat_name = stat.get('name', '')
                                    stat_value = stat.get('value', '')
                                    
                                    if stat_name == 'MIN' and stat_value:
                                        player_data['出场时间'] = stat_value
                                    elif stat_name == 'PTS' and stat_value:
                                        player_data['得分'] = stat_value
                                    elif stat_name == 'AST' and stat_value:
                                        player_data['助攻'] = stat_value
                                    elif stat_name == 'REB' and stat_value:
                                        player_data['篮板'] = stat_value
                                    elif stat_name == 'TO' and stat_value:
                                        player_data['失误'] = stat_value
                                    elif stat_name == 'FGM' and stat_value:
                                        fgm = stat_value
                                        fga = next((s.get('value', '0') for s in stats if s.get('name') == 'FGA'), '0')
                                        player_data['投篮'] = f"{fgm}-{fga}"
                                    elif stat_name == 'FG3M' and stat_value:
                                        fg3m = stat_value
                                        fg3a = next((s.get('value', '0') for s in stats if s.get('name') == 'FG3A'), '0')
                                        player_data['三分'] = f"{fg3m}-{fg3a}"
                            
                            players_data.append(player_data)
    
    # 按得分排序
    players_data.sort(key=lambda x: int(str(x['得分']).replace('-', ' ').split()[0] if '-' in str(x['得分']) else str(x['得分'])), reverse=True)
    
    return players_data

def format_minutes(minutes_str):
    """格式化出场时间"""
    if not minutes_str:
        return '0:00'
    
    if isinstance(minutes_str, str) and ':' in minutes_str:
        return minutes_str
    
    try:
        # 如果是数字，转换为MM:SS格式
        total_seconds = int(float(minutes_str) * 60)
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins}:{secs:02d}"
    except:
        return str(minutes_str)

def preload_player_data(events):
    """预加载球员数据"""
    for event in events:
        event_id = event.get('id', '')
        status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
        
        # 只预加载进行中或已结束的比赛数据
        if status_detail in ['in', 'post'] and event_id not in st.session_state.player_data_cache:
            try:
                game_details = fetch_game_details(event_id)
                if game_details:
                    st.session_state.player_data_cache[event_id] = game_details
            except:
                pass

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 查询设置")
    
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3)
    )
    
    # 自动刷新控制
    st.divider()
    st.markdown("**🔄 自动刷新**")
    auto_refresh = st.checkbox("进行中比赛自动刷新", value=st.session_state.auto_refresh)
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
    
    if st.button("🔄 立即刷新", use_container_width=True, type="primary"):
        st.session_state.player_data_cache.clear()
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    st.divider()
    st.markdown("**📊 数据说明**")
    st.caption(f"• 球员已收录: {len(NBA_PLAYERS_CN)}人")
    st.caption("• 未收录球员显示英文名")
    st.caption("• 投篮格式: 命中数-出手数")

# 主界面
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

# 获取赛程数据
schedule_data = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule_data:
    st.error("无法获取赛程数据，请检查网络连接")
    st.stop()

events = schedule_data.get('events', [])

if not events:
    st.info("今日暂无NBA比赛安排")
    st.stop()

# 预加载球员数据
preload_player_data(events)

# 统计比赛状态
live_count = 0
for event in events:
    status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
    if status_detail == 'in':
        live_count += 1

if live_count > 0:
    st.info(f"🟢 有 {live_count} 场比赛正在进行中")

# 显示比赛列表
for i, event in enumerate(events):
    event_id = event.get('id', '')
    status = event.get('status', {})
    status_detail = status.get('type', {}).get('state', 'pre')
    
    # 比赛状态
    if status_detail == 'in':
        status_badge = "🟢 进行中"
        status_color = "#10B981"
    elif status_detail == 'post':
        status_badge = "⚫ 已结束"
        status_color = "#6B7280"
    else:
        status_badge = "⏳ 未开始"
        status_color = "#3B82F6"
    
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
            away_id = away_team.get('id', '')
            home_id = home_team.get('id', '')
            
            # 创建比赛卡片
            with st.container():
                # 第一行：比分和状态
                score_col1, score_col2, score_col3, score_col4, score_col5 = st.columns([2, 1, 0.5, 1, 2])
                
                with score_col1:
                    st.markdown(f"**{away_name_cn}**")
                with score_col2:
                    st.markdown(f"<span style='color:{status_color}; font-weight:bold'>{away_score}</span>", unsafe_allow_html=True)
                with score_col3:
                    st.markdown("**VS**")
                with score_col4:
                    st.markdown(f"<span style='color:{status_color}; font-weight:bold'>{home_score}</span>", unsafe_allow_html=True)
                with score_col5:
                    st.markdown(f"**{home_name_cn}**")
                
                # 第二行：状态和时间
                col_info1, col_info2 = st.columns([3, 1])
                with col_info1:
                    st.caption(f"{status_badge} | ⏰ {game_time}")
                with col_info2:
                    if status_detail in ['in', 'post']:
                        # 检查球员数据是否可用
                        has_player_data = event_id in st.session_state.player_data_cache
                        button_disabled = not has_player_data
                        
                        button_key = f"player_btn_{event_id}"
                        button_label = "📊 显示球员数据" if not st.session_state.expanded_games.get(event_id, False) else "📊 隐藏球员数据"
                        
                        if st.button(button_label, key=button_key, type="secondary", disabled=button_disabled):
                            if event_id in st.session_state.expanded_games:
                                del st.session_state.expanded_games[event_id]
                            else:
                                st.session_state.expanded_games[event_id] = True
                            st.rerun()
                
                # 第三行：球员数据（如果展开）
                if st.session_state.expanded_games.get(event_id, False) and status_detail in ['in', 'post']:
                    # 从缓存或API获取球员数据
                    game_details = st.session_state.player_data_cache.get(event_id)
                    
                    if not game_details:
                        # 如果缓存中没有，则重新获取
                        game_details = fetch_game_details(event_id)
                        if game_details:
                            st.session_state.player_data_cache[event_id] = game_details
                    
                    if game_details:
                        # 解析球员数据
                        away_players = parse_player_stats_detailed(game_details, away_id)
                        home_players = parse_player_stats_detailed(game_details, home_id)
                        
                        if away_players or home_players:
                            # 使用两个垂直排列的容器显示球员数据
                            st.markdown(f"**{away_name_cn} 球员数据**")
                            if away_players:
                                away_df = pd.DataFrame(away_players)
                                # 确保列顺序正确
                                column_order = ['球员', '出场时间', '得分', '投篮', '三分', '助攻', '篮板', '失误']
                                available_columns = [col for col in column_order if col in away_df.columns]
                                away_df = away_df[available_columns]
                                
                                st.dataframe(
                                    away_df,
                                    hide_index=True,
                                    use_container_width=True,
                                    height=200
                                )
                            else:
                                st.info("暂无球员数据")
                            
                            st.markdown(f"**{home_name_cn} 球员数据**")
                            if home_players:
                                home_df = pd.DataFrame(home_players)
                                available_columns = [col for col in column_order if col in home_df.columns]
                                home_df = home_df[available_columns]
                                
                                st.dataframe(
                                    home_df,
                                    hide_index=True,
                                    use_container_width=True,
                                    height=200
                                )
                            else:
                                st.info("暂无球员数据")
                        else:
                            st.info("球员数据暂不可用")
                    else:
                        st.info("无法获取球员数据")
    
    # 比赛之间的分隔线
    if i < len(events) - 1:
        st.divider()

# 底部统计信息
st.divider()
st.subheader("📊 今日统计")

if events:
    status_counts = {'进行中': 0, '已结束': 0, '未开始': 0}
    for event in events:
        status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
        if status_detail == 'in':
            status_counts['进行中'] += 1
        elif status_detail == 'post':
            status_counts['已结束'] += 1
        else:
            status_counts['未开始'] += 1
    
    # 显示统计卡片
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    
    with stat_col1:
        st.metric("总比赛", len(events))
    
    with stat_col2:
        st.metric("进行中", status_counts['进行中'])
    
    with stat_col3:
        st.metric("已结束", status_counts['已结束'])

# 底部状态栏
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])

with footer_col1:
    last_refresh_str = st.session_state.last_refresh.strftime("%H:%M:%S")
    st.caption(f"🕒 最后刷新: {last_refresh_str}")

with footer_col2:
    st.caption(f"🔄 刷新次数: {st.session_state.refresh_count}")

with footer_col3:
    if st.button("🔄 手动刷新", use_container_width=True, key="footer_refresh"):
        st.session_state.player_data_cache.clear()
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = datetime.now()
        st.rerun()

# 自动刷新逻辑（只在有进行中比赛时）
if st.session_state.auto_refresh and live_count > 0:
    time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
    if time_since_refresh >= 10:  # 每10秒刷新一次
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = datetime.now()
        st.rerun()
