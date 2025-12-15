import streamlit as st
import requests
import pandas as pd
import pytz
import json
from datetime import datetime, timedelta

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
        st.error(f"获取赛程失败: {e}")
        return None

@st.cache_data(ttl=8)
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
        st.warning(f"获取比赛详情失败: {e}")
        return None

def parse_player_stats_new(game_details, team_id):
    """新版球员数据解析函数"""
    players_data = []
    
    if not game_details:
        return players_data
    
    # 调试：查看API返回的数据结构
    debug_info = st.session_state.get('debug_mode', False)
    
    # 尝试从多个可能的路径解析球员数据
    # 路径1: boxscore -> players
    boxscore = game_details.get('boxscore', {})
    players = boxscore.get('players', [])
    
    for team_players in players:
        if str(team_players.get('team', {}).get('id')) == str(team_id):
            # 获取统计类别
            statistics = team_players.get('statistics', [])
            
            # 为每个球员创建数据字典
            player_stats_map = {}
            
            # 首先收集所有球员的基本信息
            for stat_category in statistics:
                athletes = stat_category.get('athletes', [])
                for athlete_info in athletes:
                    player = athlete_info.get('athlete', {})
                    if player:
                        player_id = player.get('id', '')
                        player_name = player.get('displayName', '')
                        
                        if player_id not in player_stats_map:
                            player_stats_map[player_id] = {
                                '球员': translate_player_name(player_name),
                                '出场时间': '0:00',
                                '得分': '0',
                                '助攻': '0',
                                '篮板': '0',
                                '失误': '0'
                            }
            
            # 然后填充每个球员的统计数据
            for stat_category in statistics:
                category_name = stat_category.get('name', '')
                athletes = stat_category.get('athletes', [])
                
                for athlete_info in athletes:
                    player = athlete_info.get('athlete', {})
                    stats = athlete_info.get('stats', [])
                    
                    if player and stats:
                        player_id = player.get('id', '')
                        if player_id in player_stats_map:
                            if category_name == 'minutes':
                                # 出场时间
                                player_stats_map[player_id]['出场时间'] = format_minutes(stats[0]) if len(stats) > 0 else '0:00'
                            elif category_name == 'points':
                                # 得分
                                player_stats_map[player_id]['得分'] = str(stats[0]) if len(stats) > 0 else '0'
                            elif category_name == 'assists':
                                # 助攻
                                player_stats_map[player_id]['助攻'] = str(stats[0]) if len(stats) > 0 else '0'
                            elif category_name == 'rebounds':
                                # 篮板
                                player_stats_map[player_id]['篮板'] = str(stats[0]) if len(stats) > 0 else '0'
                            elif category_name == 'turnovers':
                                # 失误
                                player_stats_map[player_id]['失误'] = str(stats[0]) if len(stats) > 0 else '0'
            
            # 转换字典为列表
            players_data = list(player_stats_map.values())
            break
    
    # 如果上述方法没找到数据，尝试备用方法
    if not players_data:
        # 尝试从competitors中获取数据
        header = game_details.get('header', {})
        competitions = header.get('competitions', [])
        
        for competition in competitions:
            competitors = competition.get('competitors', [])
            for competitor in competitors:
                if str(competitor.get('team', {}).get('id')) == str(team_id):
                    # 尝试从其他位置获取
                    pass
    
    # 按得分排序
    players_data.sort(key=lambda x: safe_int(x['得分']), reverse=True)
    
    return players_data

def format_minutes(minutes_str):
    """格式化出场时间"""
    if not minutes_str:
        return '0:00'
    
    if isinstance(minutes_str, str) and ':' in minutes_str:
        return minutes_str
    
    try:
        # 尝试将小数分钟转换为MM:SS格式
        total_seconds = int(float(minutes_str) * 60)
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins}:{secs:02d}"
    except:
        return str(minutes_str)

def safe_int(value):
    """安全地将值转换为整数"""
    try:
        return int(str(value))
    except:
        return 0

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 查询设置")
    
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=7),
        max_value=now_beijing.date() + timedelta(days=7)
    )
    
    # 自动刷新控制
    st.divider()
    st.markdown("**🔄 自动刷新**")
    auto_refresh = st.checkbox("进行中比赛每5秒刷新", value=st.session_state.auto_refresh)
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
        st.rerun()
    
    # 调试模式
    st.session_state.debug_mode = st.checkbox("调试模式", value=False)
    
    if st.button("立即刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    st.divider()
    st.markdown("**📊 数据说明**")
    st.caption(f"• 球员已收录: {len(NBA_PLAYERS_CN)}人")
    st.caption("• 未收录球员显示英文名")
    st.caption("• 比赛数据实时更新")

# 主界面
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

# 获取数据
with st.spinner("加载赛程数据中..."):
    schedule_data = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

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
        show_details = True
    elif status_detail == 'post':
        status_badge = "⚫ 已结束"
        show_details = True
    else:
        status_badge = "⏳ 未开始"
        show_details = False
    
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
                        # 使用unique的key
                        button_key = f"player_btn_{event_id}_{i}"
                        if st.button("📊 球员数据", key=button_key, type="secondary"):
                            # 切换展开状态
                            if event_id in st.session_state.expanded_games:
                                del st.session_state.expanded_games[event_id]
                            else:
                                st.session_state.expanded_games[event_id] = True
                            st.rerun()
                
                # 第三行：球员数据（如果展开）
                if event_id in st.session_state.expanded_games and status_detail in ['in', 'post']:
                    with st.spinner("加载球员数据中..."):
                        game_details = fetch_game_details(event_id)
                        
                        if game_details:
                            # 调试模式下显示原始数据
                            if st.session_state.debug_mode:
                                with st.expander("原始数据（调试）"):
                                    st.json(game_details)
                            
                            # 使用新版解析函数
                            away_players = parse_player_stats_new(game_details, away_id)
                            home_players = parse_player_stats_new(game_details, home_id)
                            
                            if away_players or home_players:
                                # 显示球员数据
                                st.markdown(f"##### {away_name_cn} 球员数据")
                                if away_players:
                                    away_df = pd.DataFrame(away_players)
                                    # 确保列顺序正确
                                    if all(col in away_df.columns for col in ['球员', '出场时间', '得分', '助攻', '篮板', '失误']):
                                        st.dataframe(
                                            away_df[['球员', '出场时间', '得分', '助攻', '篮板', '失误']],
                                            hide_index=True,
                                            use_container_width=True,
                                            height=200
                                        )
                                    else:
                                        st.dataframe(away_df, hide_index=True, use_container_width=True)
                                else:
                                    st.info("暂无球员数据")
                                
                                st.markdown(f"##### {home_name_cn} 球员数据")
                                if home_players:
                                    home_df = pd.DataFrame(home_players)
                                    if all(col in home_df.columns for col in ['球员', '出场时间', '得分', '助攻', '篮板', '失误']):
                                        st.dataframe(
                                            home_df[['球员', '出场时间', '得分', '助攻', '篮板', '失误']],
                                            hide_index=True,
                                            use_container_width=True,
                                            height=200
                                        )
                                    else:
                                        st.dataframe(home_df, hide_index=True, use_container_width=True)
                                else:
                                    st.info("暂无球员数据")
                            else:
                                st.info("球员数据暂不可用")
                                if st.session_state.debug_mode:
                                    st.write("尝试从其他路径获取数据...")
                        else:
                            st.info("无法获取比赛详情数据")
    
    # 比赛之间的分隔线
    if i < len(events) - 1:
        st.divider()

# 右侧统计信息
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
    if st.button("🔄 手动刷新", use_container_width=True, key="manual_refresh"):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = datetime.now()
        st.rerun()

# 检查是否需要自动刷新
if st.session_state.auto_refresh:
    # 检查是否有进行中的比赛
    schedule_data_refresh = fetch_nba_schedule(today_str)
    if schedule_data_refresh:
        events_refresh = schedule_data_refresh.get('events', [])
        live_games = 0
        for event in events_refresh:
            status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
            if status_detail == 'in':
                live_games += 1
        
        if live_games > 0:
            # 计算距离上次刷新的时间
            time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
            if time_since_refresh >= 5:
                # 自动刷新
                st.session_state.refresh_count += 1
                st.session_state.last_refresh = datetime.now()
                st.rerun()
