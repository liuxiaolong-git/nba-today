import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import time

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
if 'schedule_cache' not in st.session_state:
    st.session_state.schedule_cache = None
if 'schedule_cache_time' not in st.session_state:
    st.session_state.schedule_cache_time = None

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)
today_str = now_beijing.strftime('%Y-%m-%d')

# NBA球队中英文对照表
NBA_TEAMS_CN = {
    "Atlanta Hawks": "亚特兰大老鹰", "Boston Celtics": "波士顿凯尔特人",
    "Brooklyn Nets": "布鲁克林篮网", "Charlotte Hornets": "夏洛特黄蜂",
    "Chicago Bulls": "芝加哥公牛", "Cleveland Cavaliers": "克里夫兰骑士",
    "Detroit Pistons": "底特律活塞", "Indiana Pacers": "印第安纳步行者",
    "Miami Heat": "迈阿密热火", "Milwaukee Bucks": "密尔沃基雄鹿",
    "New York Knicks": "纽约尼克斯", "Orlando Magic": "奥兰多魔术",
    "Philadelphia 76ers": "费城76人", "Toronto Raptors": "多伦多猛龙",
    "Washington Wizards": "华盛顿奇才", "Dallas Mavericks": "达拉斯独行侠",
    "Denver Nuggets": "丹佛掘金", "Golden State Warriors": "金州勇士",
    "Houston Rockets": "休斯顿火箭", "LA Clippers": "洛杉矶快船",
    "Los Angeles Lakers": "洛杉矶湖人", "Memphis Grizzlies": "孟菲斯灰熊",
    "Minnesota Timberwolves": "明尼苏达森林狼", "New Orleans Pelicans": "新奥尔良鹈鹕",
    "Oklahoma City Thunder": "俄克拉荷马雷霆", "Phoenix Suns": "菲尼克斯太阳",
    "Portland Trail Blazers": "波特兰开拓者", "Sacramento Kings": "萨克拉门托国王",
    "San Antonio Spurs": "圣安东尼奥马刺", "Utah Jazz": "犹他爵士"
}

# NBA球员中英文对照表
NBA_PLAYERS_CN = {
    "LeBron James": "勒布朗·詹姆斯", "Anthony Davis": "安东尼·戴维斯",
    "Stephen Curry": "斯蒂芬·库里", "Klay Thompson": "克莱·汤普森",
    "Kevin Durant": "凯文·杜兰特", "James Harden": "詹姆斯·哈登",
    "Giannis Antetokounmpo": "扬尼斯·阿德托昆博", "Luka Doncic": "卢卡·东契奇",
    "Nikola Jokic": "尼古拉·约基奇", "Joel Embiid": "乔尔·恩比德",
    "Jayson Tatum": "杰森·塔图姆", "Damian Lillard": "达米安·利拉德",
    "Kawhi Leonard": "科怀·伦纳德", "Paul George": "保罗·乔治",
    "Donovan Mitchell": "多诺万·米切尔", "Trae Young": "特雷·杨",
    "Zion Williamson": "蔡恩·威廉森", "Ja Morant": "贾·莫兰特",
    "Devin Booker": "德文·布克", "Chris Paul": "克里斯·保罗",
    "Kyrie Irving": "凯里·欧文", "Russell Westbrook": "拉塞尔·威斯布鲁克",
    "Anthony Edwards": "安东尼·爱德华兹", "Jalen Brunson": "杰伦·布伦森",
    
    # 示例中的球员
    "Darius Garland": "达柳斯·加兰", "Jaylon Tyson": "杰伦·泰森",
    "Dean Wade": "迪安·韦德", "Thomas Bryant": "托马斯·布莱恩特",
    "Jarrett Allen": "贾勒特·阿伦", "Lonzo Ball": "朗佐·鲍尔",
    "Nae'Qwan Tomlin": "内昆·汤姆林", "De'Andre Hunter": "德安德烈·亨特",
    "Craig Porter": "克雷格·波特"
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

def fetch_nba_schedule_cached(date_str):
    """获取NBA赛程数据（带缓存）"""
    cache_key = f"schedule_{date_str}"
    
    # 检查缓存是否有效（5秒内）
    if (st.session_state.schedule_cache_time and 
        cache_key in st.session_state.player_data_cache and
        (datetime.now() - st.session_state.schedule_cache_time).total_seconds() < 5):
        return st.session_state.player_data_cache[cache_key]
    
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
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # 缓存数据
        st.session_state.player_data_cache[cache_key] = data
        st.session_state.schedule_cache_time = datetime.now()
        
        return data
        
    except Exception as e:
        st.error(f"获取赛程失败: {e}")
        return None

def fetch_game_details_cached(game_id):
    """获取比赛详细数据（带缓存）"""
    cache_key = f"game_{game_id}"
    
    # 检查缓存
    if cache_key in st.session_state.player_data_cache:
        cached_time = st.session_state.player_data_cache.get(f"{cache_key}_time")
        if cached_time and (datetime.now() - cached_time).total_seconds() < 3:
            return st.session_state.player_data_cache[cache_key]
    
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        params = {'event': game_id}
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # 缓存数据
        st.session_state.player_data_cache[cache_key] = data
        st.session_state.player_data_cache[f"{cache_key}_time"] = datetime.now()
        
        return data
        
    except Exception as e:
        return None

def parse_player_stats_fast(game_details, team_id):
    """快速球员数据解析函数"""
    players_data = []
    
    if not game_details:
        return players_data
    
    # 尝试从boxscore中获取数据
    boxscore = game_details.get('boxscore', {})
    players = boxscore.get('players', [])
    
    for team_players in players:
        if str(team_players.get('team', {}).get('id')) == str(team_id):
            statistics = team_players.get('statistics', [])
            
            # 首先收集所有球员
            player_map = {}
            for stat_category in statistics:
                athletes = stat_category.get('athletes', [])
                for athlete_info in athletes:
                    player = athlete_info.get('athlete', {})
                    if player:
                        player_id = player.get('id', '')
                        if player_id not in player_map:
                            player_name = player.get('displayName', '')
                            player_map[player_id] = {
                                '球员': translate_player_name(player_name),
                                '出场时间': '0:00',
                                '得分': '0',
                                '助攻': '0',
                                '篮板': '0',
                                '失误': '0'
                            }
            
            # 然后填充统计数据
            for stat_category in statistics:
                category_name = stat_category.get('name', '')
                athletes = stat_category.get('athletes', [])
                
                for athlete_info in athletes:
                    player = athlete_info.get('athlete', {})
                    stats = athlete_info.get('stats', [])
                    
                    if player and stats:
                        player_id = player.get('id', '')
                        if player_id in player_map:
                            if category_name == 'minutes' and len(stats) > 0:
                                player_map[player_id]['出场时间'] = stats[0] or '0:00'
                            elif category_name == 'points' and len(stats) > 0:
                                player_map[player_id]['得分'] = stats[0] or '0'
                            elif category_name == 'assists' and len(stats) > 0:
                                player_map[player_id]['助攻'] = stats[0] or '0'
                            elif category_name == 'rebounds' and len(stats) > 0:
                                player_map[player_id]['篮板'] = stats[0] or '0'
                            elif category_name == 'turnovers' and len(stats) > 0:
                                player_map[player_id]['失误'] = stats[0] or '0'
            
            players_data = list(player_map.values())
            break
    
    # 按得分排序
    players_data.sort(key=lambda x: int(str(x['得分']).replace(':', '').split('-')[0] if isinstance(x['得分'], str) else 0), reverse=True)
    return players_data

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
    st.caption("• 数据已缓存优化")

# 主界面
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

# 获取数据（使用缓存）
start_time = time.time()
schedule_data = fetch_nba_schedule_cached(selected_date.strftime('%Y-%m-%d'))

if not schedule_data:
    st.error("无法获取赛程数据，请检查网络连接")
    st.stop()

events = schedule_data.get('events', [])

if not events:
    st.info("今日暂无NBA比赛安排")
    st.stop()

# 统计比赛状态
live_count = 0
for event in events:
    status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
    if status_detail == 'in':
        live_count += 1

# 显示比赛列表
for i, event in enumerate(events):
    event_id = event.get('id', '')
    status = event.get('status', {})
    status_detail = status.get('type', {}).get('state', 'pre')
    
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
            away_id = away_team.get('id', '')
            home_id = home_team.get('id', '')
            
            # 创建比赛卡片
            with st.container():
                # 第一行：比分和状态
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
                
                # 第二行：状态和时间
                info_col1, info_col2 = st.columns([3, 1])
                with info_col1:
                    st.caption(f"{status_badge} | ⏰ {game_time}")
                with info_col2:
                    if status_detail in ['in', 'post']:
                        button_key = f"player_btn_{event_id}"
                        if st.button("📊 球员数据", key=button_key, type="secondary"):
                            if event_id in st.session_state.expanded_games:
                                del st.session_state.expanded_games[event_id]
                            else:
                                st.session_state.expanded_games[event_id] = True
                            st.rerun()
                
                # 第三行：球员数据（如果展开）
                if event_id in st.session_state.expanded_games and status_detail in ['in', 'post']:
                    # 预加载球员数据（不显示spinner）
                    game_details = fetch_game_details_cached(event_id)
                    
                    if game_details:
                        # 快速解析球员数据
                        away_players = parse_player_stats_fast(game_details, away_id)
                        home_players = parse_player_stats_fast(game_details, home_id)
                        
                        if away_players or home_players:
                            # 使用tabs显示球员数据
                            tab1, tab2 = st.tabs([f"{away_name_cn} 球员", f"{home_name_cn} 球员"])
                            
                            with tab1:
                                if away_players:
                                    # 清理数据格式
                                    for player in away_players:
                                        for key in ['得分', '助攻', '篮板', '失误']:
                                            if isinstance(player[key], str) and '-' in player[key]:
                                                # 处理 "3-7" 这样的格式，取第一个数字
                                                player[key] = player[key].split('-')[0]
                                    
                                    away_df = pd.DataFrame(away_players)
                                    st.dataframe(
                                        away_df[['球员', '出场时间', '得分', '助攻', '篮板', '失误']],
                                        hide_index=True,
                                        use_container_width=True,
                                        height=250
                                    )
                                else:
                                    st.info("暂无球员数据")
                            
                            with tab2:
                                if home_players:
                                    # 清理数据格式
                                    for player in home_players:
                                        for key in ['得分', '助攻', '篮板', '失误']:
                                            if isinstance(player[key], str) and '-' in player[key]:
                                                player[key] = player[key].split('-')[0]
                                    
                                    home_df = pd.DataFrame(home_players)
                                    st.dataframe(
                                        home_df[['球员', '出场时间', '得分', '助攻', '篮板', '失误']],
                                        hide_index=True,
                                        use_container_width=True,
                                        height=250
                                    )
                                else:
                                    st.info("暂无球员数据")
                        else:
                            st.info("球员数据暂不可用")
    
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
