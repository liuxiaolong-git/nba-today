import streamlit as st
import requests
import pandas as pd
import pytz
import time
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
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = False

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

# 增强版球员翻译字典
NBA_PLAYERS_CN = {
    # 湖人
    "LeBron James": "勒布朗·詹姆斯", "Anthony Davis": "安东尼·戴维斯",
    "D'Angelo Russell": "丹吉洛·拉塞尔", "Austin Reaves": "奥斯汀·里夫斯",
    "Rui Hachimura": "八村垒", "Jarred Vanderbilt": "贾里德·范德比尔特",
    
    # 勇士
    "Stephen Curry": "斯蒂芬·库里", "Klay Thompson": "克莱·汤普森",
    "Draymond Green": "德雷蒙德·格林", "Andrew Wiggins": "安德鲁·威金斯",
    "Chris Paul": "克里斯·保罗", "Jonathan Kuminga": "乔纳森·库明加",
    
    # 凯尔特人
    "Jayson Tatum": "杰森·塔图姆", "Jaylen Brown": "杰伦·布朗",
    "Kristaps Porzingis": "克里斯塔普斯·波尔津吉斯", "Derrick White": "德里克·怀特",
    "Jrue Holiday": "朱·霍勒迪",
    
    # 掘金
    "Nikola Jokic": "尼古拉·约基奇", "Jamal Murray": "贾马尔·穆雷",
    "Aaron Gordon": "阿隆·戈登", "Michael Porter Jr.": "小迈克尔·波特",
    
    # 太阳
    "Kevin Durant": "凯文·杜兰特", "Devin Booker": "德文·布克",
    "Bradley Beal": "布拉德利·比尔",
    
    # 雄鹿
    "Giannis Antetokounmpo": "扬尼斯·阿德托昆博", "Damian Lillard": "达米安·利拉德",
    "Khris Middleton": "克里斯·米德尔顿",
    
    # 76人
    "Joel Embiid": "乔尔·恩比德", "Tyrese Maxey": "泰瑞斯·马克西",
    "Tobias Harris": "托拜厄斯·哈里斯",
    
    # 快船
    "Kawhi Leonard": "科怀·伦纳德", "Paul George": "保罗·乔治",
    "James Harden": "詹姆斯·哈登", "Russell Westbrook": "拉塞尔·威斯布鲁克",
    
    # 骑士
    "Donovan Mitchell": "多诺万·米切尔", "Darius Garland": "达柳斯·加兰",
    "Evan Mobley": "埃文·莫布利", "Jarrett Allen": "贾勒特·阿伦",
    
    # 其他球队核心球员
    "Luka Doncic": "卢卡·东契奇", "Kyrie Irving": "凯里·欧文",
    "Shai Gilgeous-Alexander": "谢伊·吉尔杰斯-亚历山大",
    "Chet Holmgren": "切特·霍姆格伦", "Anthony Edwards": "安东尼·爱德华兹",
    "Karl-Anthony Towns": "卡尔-安东尼·唐斯", "Rudy Gobert": "鲁迪·戈贝尔",
    "Zion Williamson": "蔡恩·威廉森", "Brandon Ingram": "布兰登·英格拉姆",
    "Trae Young": "特雷·杨", "Dejounte Murray": "德章泰·穆雷",
    "De'Aaron Fox": "达龙·福克斯", "Domantas Sabonis": "多曼塔斯·萨博尼斯",
    "LaMelo Ball": "拉梅洛·鲍尔", "Miles Bridges": "迈尔斯·布里奇斯",
    "Scottie Barnes": "斯科蒂·巴恩斯", "Pascal Siakam": "帕斯卡尔·西亚卡姆",
    "Jalen Brunson": "杰伦·布伦森", "Julius Randle": "朱利叶斯·兰德尔",
    "Jimmy Butler": "吉米·巴特勒", "Bam Adebayo": "巴姆·阿德巴约",
    "Ja Morant": "贾·莫兰特", "Jaren Jackson Jr.": "小贾伦·杰克逊",
    "Victor Wembanyama": "维克托·文班亚马",
    
    # 示例中的球员
    "Jaylon Tyson": "杰伦·泰森", "Dean Wade": "迪安·韦德",
    "Thomas Bryant": "托马斯·布莱恩特", "Lonzo Ball": "朗佐·鲍尔",
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
        return None

def parse_player_stats_simple(game_details, team_id):
    """简化的球员数据解析函数"""
    players_data = []
    
    if not game_details:
        return players_data
    
    # 查找球员统计数据
    boxscore = game_details.get('boxscore', {})
    players = boxscore.get('players', [])
    
    for team_players in players:
        if str(team_players.get('team', {}).get('id')) == str(team_id):
            for stat_category in team_players.get('statistics', []):
                athletes = stat_category.get('athletes', [])
                
                for athlete_info in athletes:
                    player = athlete_info.get('athlete', {})
                    stats = athlete_info.get('stats', [])
                    
                    if player and stats:
                        player_name = player.get('displayName', '')
                        player_name_cn = translate_player_name(player_name)
                        
                        # 根据不同统计类别解析数据
                        category_name = stat_category.get('name', '')
                        
                        # 查找现有球员或创建新条目
                        existing_player = next((p for p in players_data if p['球员'] == player_name_cn), None)
                        if not existing_player:
                            existing_player = {
                                '球员': player_name_cn,
                                '出场时间': '0:00',
                                '得分': '0',
                                '助攻': '0',
                                '篮板': '0',
                                '失误': '0'
                            }
                            players_data.append(existing_player)
                        
                        # 更新数据
                        if category_name == 'minutes' and len(stats) > 0:
                            existing_player['出场时间'] = format_minutes(stats[0])
                        elif category_name == 'points' and len(stats) > 0:
                            existing_player['得分'] = clean_number(stats[0])
                        elif category_name == 'assists' and len(stats) > 0:
                            existing_player['助攻'] = clean_number(stats[0])
                        elif category_name == 'rebounds' and len(stats) > 0:
                            existing_player['篮板'] = clean_number(stats[0])
                        elif category_name == 'turnovers' and len(stats) > 0:
                            existing_player['失误'] = clean_number(stats[0])
    
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
        total_seconds = int(float(minutes_str) * 60)
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins}:{secs:02d}"
    except:
        return str(minutes_str)

def clean_number(value):
    """清理数字格式"""
    if not value:
        return '0'
    
    if isinstance(value, (int, float)):
        return str(int(value))
    
    # 移除非数字字符
    clean_str = ''.join(c for c in str(value) if c.isdigit() or c == '-')
    
    if not clean_str or clean_str == '-':
        return '0'
    
    if clean_str.startswith('-'):
        return str(abs(int(clean_str)))
    
    return str(int(float(clean_str)))

def safe_int(value):
    """安全地将值转换为整数"""
    try:
        return int(clean_number(value))
    except:
        return 0

# 检查是否需要自动刷新
if st.session_state.auto_refresh:
    # 检查是否有进行中的比赛需要刷新
    schedule_data = fetch_nba_schedule(today_str)
    if schedule_data:
        events = schedule_data.get('events', [])
        live_games = 0
        for event in events:
            status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
            if status_detail == 'in':
                live_games += 1
        
        if live_games > 0:
            # 计算距离上次刷新的时间
            time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
            if time_since_refresh >= 5:
                # 设置刷新触发器
                st.session_state.refresh_trigger = True

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

# 主界面 - 紧凑布局
col1, col2 = st.columns([3, 1])

with col1:
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

    # 紧凑显示比赛
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
                
                # 创建比赛卡片容器
                with st.container():
                    # 紧凑的比赛卡片
                    col_team1, col_score1, col_vs, col_score2, col_team2 = st.columns([2.5, 0.8, 0.5, 0.8, 2.5])
                    
                    with col_team1:
                        st.markdown(f"**{away_name_cn}**")
                    
                    with col_score1:
                        st.markdown(f"**{away_score}**")
                    
                    with col_vs:
                        st.markdown("**VS**")
                    
                    with col_score2:
                        st.markdown(f"**{home_score}**")
                    
                    with col_team2:
                        st.markdown(f"**{home_name_cn}**")
                    
                    # 比赛信息行
                    col_info1, col_info2 = st.columns([3, 1])
                    with col_info1:
                        st.caption(f"{status_badge} | ⏰ {game_time}")
                    
                    with col_info2:
                        # 使用expander来显示/隐藏球员数据
                        expander_key = f"exp_{event_id}"
                        
                        # 检查是否需要自动展开（进行中和已结束的比赛）
                        if status_detail in ['in', 'post']:
                            with st.expander("📊 球员数据", expanded=False):
                                # 获取球员数据
                                with st.spinner("加载球员数据..."):
                                    game_details = fetch_game_details(event_id)
                                    
                                    if game_details:
                                        away_players = parse_player_stats_simple(game_details, away_id)
                                        home_players = parse_player_stats_simple(game_details, home_id)
                                        
                                        if away_players or home_players:
                                            # 使用columns显示两队数据
                                            player_col1, player_col2 = st.columns(2)
                                            
                                            with player_col1:
                                                if away_players:
                                                    st.markdown(f"**{away_name_cn}**")
                                                    away_df = pd.DataFrame(away_players)
                                                    st.dataframe(
                                                        away_df[['球员', '出场时间', '得分', '助攻', '篮板', '失误']],
                                                        hide_index=True,
                                                        use_container_width=True,
                                                        height=200
                                                    )
                                            
                                            with player_col2:
                                                if home_players:
                                                    st.markdown(f"**{home_name_cn}**")
                                                    home_df = pd.DataFrame(home_players)
                                                    st.dataframe(
                                                        home_df[['球员', '出场时间', '得分', '助攻', '篮板', '失误']],
                                                        hide_index=True,
                                                        use_container_width=True,
                                                        height=200
                                                    )
                                        else:
                                            st.info("球员数据暂不可用")
                                    else:
                                        st.info("无法获取球员数据")
                        else:
                            st.caption("比赛开始后显示球员数据")
        
        # 比赛之间的分隔线
        if i < len(events) - 1:
            st.divider()

with col2:
    st.subheader("📈 今日统计")
    
    # 统计信息
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
        st.metric("总比赛", len(events))
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("进行中", status_counts['进行中'])
        with col_b:
            st.metric("已结束", status_counts['已结束'])
        
        st.metric("未开始", status_counts['未开始'])
        
        # 显示高分比赛
        st.markdown("**🔥 高分比赛**")
        high_score_games = []
        for event in events:
            competitions = event.get('competitions', [])
            if competitions:
                competitors = competitions[0].get('competitors', [])
                if len(competitors) >= 2:
                    away_score = safe_int(competitors[0].get('score', '0'))
                    home_score = safe_int(competitors[1].get('score', '0'))
                    total_score = away_score + home_score
                    
                    if total_score > 200:
                        away_name = translate_team_name(competitors[0].get('team', {}).get('displayName', ''))
                        home_name = translate_team_name(competitors[1].get('team', {}).get('displayName', ''))
                        high_score_games.append(f"{away_score}-{home_score}")
        
        if high_score_games:
            for score in high_score_games[:3]:
                st.write(f"• {score}")
        else:
            st.info("暂无高分比赛")

# 底部状态栏
st.divider()
footer_cols = st.columns([2, 1, 1])
with footer_cols[0]:
    last_refresh_str = st.session_state.last_refresh.strftime("%H:%M:%S")
    st.caption(f"🕒 最后刷新: {last_refresh_str}")
with footer_cols[1]:
    st.caption(f"🔄 刷新次数: {st.session_state.refresh_count}")
with footer_cols[2]:
    if st.button("🔄 手动刷新", use_container_width=True, key="manual_refresh"):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = datetime.now()
        st.rerun()

# 处理自动刷新
if st.session_state.refresh_trigger:
    st.session_state.refresh_trigger = False
    st.session_state.refresh_count += 1
    st.session_state.last_refresh = datetime.now()
    st.rerun()

# 显示自动刷新状态
if st.session_state.auto_refresh and live_count > 0:
    refresh_time = 5 - (datetime.now() - st.session_state.last_refresh).total_seconds()
    if refresh_time > 0:
        st.caption(f"⏳ 自动刷新倒计时: {int(refresh_time)}秒")
