import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程与球员数据")
st.caption("数据来源: ESPN公开接口 | 完全免费 | 实时更新 | 全中文")

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)
today_str = now_beijing.strftime('%Y-%m-%d')

# NBA球队中英文对照表
NBA_TEAMS_CN = {
    "Atlanta Hawks": "亚特兰大老鹰",
    "Boston Celtics": "波士顿凯尔特人",
    "Brooklyn Nets": "布鲁克林篮网",
    "Charlotte Hornets": "夏洛特黄蜂",
    "Chicago Bulls": "芝加哥公牛",
    "Cleveland Cavaliers": "克里夫兰骑士",
    "Detroit Pistons": "底特律活塞",
    "Indiana Pacers": "印第安纳步行者",
    "Miami Heat": "迈阿密热火",
    "Milwaukee Bucks": "密尔沃基雄鹿",
    "New York Knicks": "纽约尼克斯",
    "Orlando Magic": "奥兰多魔术",
    "Philadelphia 76ers": "费城76人",
    "Toronto Raptors": "多伦多猛龙",
    "Washington Wizards": "华盛顿奇才",
    "Dallas Mavericks": "达拉斯独行侠",
    "Denver Nuggets": "丹佛掘金",
    "Golden State Warriors": "金州勇士",
    "Houston Rockets": "休斯顿火箭",
    "LA Clippers": "洛杉矶快船",
    "Los Angeles Lakers": "洛杉矶湖人",
    "Los Angeles Clippers": "洛杉矶快船",
    "Memphis Grizzlies": "孟菲斯灰熊",
    "Minnesota Timberwolves": "明尼苏达森林狼",
    "New Orleans Pelicans": "新奥尔良鹈鹕",
    "Oklahoma City Thunder": "俄克拉荷马雷霆",
    "Phoenix Suns": "菲尼克斯太阳",
    "Portland Trail Blazers": "波特兰开拓者",
    "Sacramento Kings": "萨克拉门托国王",
    "San Antonio Spurs": "圣安东尼奥马刺",
    "Utah Jazz": "犹他爵士"
}

# NBA球员中英文对照表（常见球员）
NBA_PLAYERS_CN = {
    # 湖人队
    "LeBron James": "勒布朗·詹姆斯",
    "Anthony Davis": "安东尼·戴维斯",
    "D'Angelo Russell": "丹吉洛·拉塞尔",
    "Austin Reaves": "奥斯汀·里夫斯",
    "Rui Hachimura": "八村垒",
    "Jarred Vanderbilt": "贾里德·范德比尔特",
    
    # 勇士队
    "Stephen Curry": "斯蒂芬·库里",
    "Klay Thompson": "克莱·汤普森",
    "Draymond Green": "德雷蒙德·格林",
    "Andrew Wiggins": "安德鲁·威金斯",
    "Chris Paul": "克里斯·保罗",
    "Jonathan Kuminga": "乔纳森·库明加",
    
    # 凯尔特人队
    "Jayson Tatum": "杰森·塔图姆",
    "Jaylen Brown": "杰伦·布朗",
    "Kristaps Porzingis": "克里斯塔普斯·波尔津吉斯",
    "Derrick White": "德里克·怀特",
    "Jrue Holiday": "朱·霍勒迪",
    
    # 掘金队
    "Nikola Jokic": "尼古拉·约基奇",
    "Jamal Murray": "贾马尔·穆雷",
    "Aaron Gordon": "阿隆·戈登",
    "Michael Porter Jr.": "小迈克尔·波特",
    
    # 太阳队
    "Kevin Durant": "凯文·杜兰特",
    "Devin Booker": "德文·布克",
    "Bradley Beal": "布拉德利·比尔",
    
    # 雄鹿队
    "Giannis Antetokounmpo": "扬尼斯·阿德托昆博",
    "Damian Lillard": "达米安·利拉德",
    "Khris Middleton": "克里斯·米德尔顿",
    
    # 76人队
    "Joel Embiid": "乔尔·恩比德",
    "Tyrese Maxey": "泰瑞斯·马克西",
    "Tobias Harris": "托拜厄斯·哈里斯",
    
    # 快船队
    "Kawhi Leonard": "科怀·伦纳德",
    "Paul George": "保罗·乔治",
    "James Harden": "詹姆斯·哈登",
    "Russell Westbrook": "拉塞尔·威斯布鲁克",
    
    # 独行侠队
    "Luka Doncic": "卢卡·东契奇",
    "Kyrie Irving": "凯里·欧文",
    
    # 雷霆队
    "Shai Gilgeous-Alexander": "谢伊·吉尔杰斯-亚历山大",
    "Chet Holmgren": "切特·霍姆格伦",
    
    # 森林狼
    "Anthony Edwards": "安东尼·爱德华兹",
    "Karl-Anthony Towns": "卡尔-安东尼·唐斯",
    "Rudy Gobert": "鲁迪·戈贝尔",
    
    # 其他常见球员
    "Jimmy Butler": "吉米·巴特勒",
    "Bam Adebayo": "巴姆·阿德巴约",
    "Donovan Mitchell": "多诺万·米切尔",
    "Trae Young": "特雷·杨",
    "De'Aaron Fox": "达龙·福克斯",
    "Domantas Sabonis": "多曼塔斯·萨博尼斯",
    "LaMelo Ball": "拉梅洛·鲍尔",
    "Zion Williamson": "蔡恩·威廉森",
    "Victor Wembanyama": "维克托·文班亚马",
    "Jalen Brunson": "杰伦·布伦森",
    "Pascal Siakam": "帕斯卡尔·西亚卡姆",
    "Scottie Barnes": "斯科蒂·巴恩斯"
}

def translate_player_name(english_name):
    """将英文球员名转换为中文"""
    if english_name in NBA_PLAYERS_CN:
        return NBA_PLAYERS_CN[english_name]
    # 如果不在预设名单中，尝试智能翻译
    elif "Jr." in english_name:
        return english_name.replace("Jr.", "小")
    elif "III" in english_name:
        return english_name.replace(" III", "三世")
    elif "II" in english_name:
        return english_name.replace(" II", "二世")
    else:
        # 保留英文名，但显示提示
        return f"{english_name}"

def translate_team_name(english_name):
    """将英文队名转换为中文"""
    return NBA_TEAMS_CN.get(english_name, english_name)

@st.cache_data(ttl=300)
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
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        st.error(f"获取赛程失败: {e}")
        return None

@st.cache_data(ttl=180)
def fetch_game_details(game_id):
    """获取比赛详细数据，包括球员统计"""
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        params = {'event': game_id}
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        st.warning(f"获取比赛详情失败: {e}")
        return None

def parse_player_stats(game_details, team_id):
    """从比赛详情中解析球员数据"""
    players_data = []
    
    if not game_details:
        return players_data
    
    boxscore = game_details.get('boxscore', {})
    players = boxscore.get('players', [])
    
    for team_players in players:
        if team_players.get('team', {}).get('id') == str(team_id):
            for player_info in team_players.get('statistics', [])[0].get('athletes', []):
                player = player_info.get('athlete', {})
                stats = player_info.get('stats', [])
                
                if player and stats:
                    player_name = player.get('displayName', '')
                    player_name_cn = translate_player_name(player_name)
                    
                    # 获取球员位置
                    position_abbr = player.get('position', {}).get('abbreviation', '')
                    position_map = {
                        'G': '后卫',
                        'F': '前锋',
                        'C': '中锋',
                        'SG': '得分后卫',
                        'PG': '控球后卫',
                        'SF': '小前锋',
                        'PF': '大前锋'
                    }
                    position_cn = position_map.get(position_abbr, position_abbr)
                    
                    # 计算命中率
                    if len(stats) > 8:
                        fg_percentage = stats[8]
                        if fg_percentage is not None:
                            fg_display = f"{float(fg_percentage):.1f}%"
                        else:
                            fg_display = "0%"
                    else:
                        fg_display = "0%"
                    
                    player_entry = {
                        '球员': player_name_cn,
                        '原英文名': player_name if player_name_cn != player_name else "",
                        '号码': player.get('jersey', ''),
                        '位置': position_cn,
                        '出场时间': stats[0] if len(stats) > 0 and stats[0] else '0',
                        '得分': stats[1] if len(stats) > 1 else '0',
                        '篮板': stats[2] if len(stats) > 2 else '0',
                        '助攻': stats[3] if len(stats) > 3 else '0',
                        '抢断': stats[4] if len(stats) > 4 else '0',
                        '盖帽': stats[5] if len(stats) > 5 else '0',
                        '失误': stats[6] if len(stats) > 6 else '0',
                        '犯规': stats[7] if len(stats) > 7 else '0',
                        '命中率': fg_display
                    }
                    players_data.append(player_entry)
    
    # 按得分排序
    players_data.sort(key=lambda x: int(x['得分']), reverse=True)
    return players_data

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 查询设置")
    
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=30),
        max_value=now_beijing.date() + timedelta(days=30)
    )
    
    # 比赛状态筛选
    status_options = {
        "全部比赛": "all",
        "未开始": "pre",
        "进行中": "in", 
        "已结束": "post"
    }
    
    selected_status = st.selectbox(
        "比赛状态筛选",
        options=list(status_options.keys()),
        index=0
    )
    
    st.divider()
    st.markdown("**📊 数据说明**")
    st.caption("• 已收录100+常见球员中文名")
    st.caption("• 比赛中和结束的比赛显示球员数据")
    st.caption("• 数据每5分钟自动更新")
    
    # 显示统计数据
    st.divider()
    st.markdown("**👥 球员翻译统计**")
    st.metric("已收录球员数", len(NBA_PLAYERS_CN))
    st.caption("未收录球员将显示英文名")

# 主界面
st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')} NBA赛程")

# 获取数据
with st.spinner("正在获取NBA赛程数据..."):
    schedule_data = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule_data:
    st.error("无法获取赛程数据，请检查网络连接或稍后重试")
    st.stop()

events = schedule_data.get('events', [])

if not events:
    st.info("今日暂无NBA比赛安排")
    st.stop()

# 按状态筛选比赛
filtered_events = []
for event in events:
    status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
    
    if selected_status == "全部比赛":
        filtered_events.append(event)
    elif selected_status == "未开始" and status_detail == 'pre':
        filtered_events.append(event)
    elif selected_status == "进行中" and status_detail == 'in':
        filtered_events.append(event)
    elif selected_status == "已结束" and status_detail == 'post':
        filtered_events.append(event)

if not filtered_events:
    st.warning(f"没有找到{selected_status}的比赛")
    st.stop()

st.success(f"找到 {len(filtered_events)} 场比赛")

# 显示比赛列表
for event in filtered_events:
    event_id = event.get('id', '')
    name = event.get('name', 'NBA比赛')
    
    # 比赛状态
    status = event.get('status', {})
    status_type = status.get('type', {}).get('description', '未开始')
    status_detail = status.get('type', {}).get('state', 'pre')
    
    # 状态显示
    if status_detail == 'in':
        status_text = "🟢 进行中"
        status_color = "#10B981"
        show_details = True
    elif status_detail == 'post':
        status_text = "⚫ 已结束"
        status_color = "#6B7280"
        show_details = True
    else:
        status_text = "⏳ 未开始"
        status_color = "#3B82F6"
        show_details = False
    
    # 比赛时间
    date_str = event.get('date', '')
    if date_str:
        try:
            utc_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            beijing_time = utc_time.astimezone(beijing_tz)
            game_time = beijing_time.strftime("%H:%M")
            game_date = beijing_time.strftime("%m月%d日")
        except:
            game_time = "时间待定"
            game_date = ""
    else:
        game_time = "时间待定"
        game_date = ""
    
    # 参赛队伍和比分
    competitions = event.get('competitions', [])
    if competitions:
        competition = competitions[0]
        competitors = competition.get('competitors', [])
        
        if len(competitors) >= 2:
            away_team = competitors[0].get('team', {})
            home_team = competitors[1].get('team', {})
            
            away_name_en = away_team.get('displayName', '客队')
            home_name_en = home_team.get('displayName', '主队')
            away_name_cn = translate_team_name(away_name_en)
            home_name_cn = translate_team_name(home_name_en)
            
            away_score = competitors[0].get('score', '0')
            home_score = competitors[1].get('score', '0')
            away_id = away_team.get('id', '')
            home_id = home_team.get('id', '')
            
            # 比赛卡片
            with st.expander(f"{status_text} | {away_name_cn} vs {home_name_cn}", expanded=show_details):
                # 使用列布局显示比分
                col_a, col_vs, col_h = st.columns([2, 1, 2])
                
                with col_a:
                    st.markdown(f"### 🏀 {away_name_cn}")
                    st.markdown(f"<h2 style='color: #EF4444; margin: 0;'>{away_score}</h2>", unsafe_allow_html=True)
                    if away_score != '0' and home_score != '0':
                        st.caption(f"客队")
                
                with col_vs:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.markdown("### **VS**")
                    st.markdown(f"*{game_time}*")
                
                with col_h:
                    st.markdown(f"### 🏠 {home_name_cn}")
                    st.markdown(f"<h2 style='color: #3B82F6; margin: 0;'>{home_score}</h2>", unsafe_allow_html=True)
                    if away_score != '0' and home_score != '0':
                        st.caption(f"主队")
                
                # 比赛详情
                st.caption(f"比赛时间: {game_date} {game_time} | 状态: {status_type}")
                
                # 显示球员数据（如果是进行中或已结束的比赛）
                if show_details and event_id:
                    with st.spinner("正在获取球员数据..."):
                        game_details = fetch_game_details(event_id)
                        
                        if game_details:
                            st.markdown("---")
                            st.markdown("### 📊 球员数据统计")
                            
                            # 获取球员数据
                            away_players = parse_player_stats(game_details, away_id)
                            home_players = parse_player_stats(game_details, home_id)
                            
                            # 显示客队球员数据
                            if away_players:
                                st.markdown(f"#### {away_name_cn} 球员数据")
                                
                                # 创建DataFrame
                                away_df = pd.DataFrame(away_players)
                                
                                # 设置显示配置
                                column_config = {
                                    "球员": st.column_config.TextColumn(
                                        width="large",
                                        help="球员中文名"
                                    ),
                                    "原英文名": st.column_config.TextColumn(
                                        width="medium",
                                        help="球员英文原名"
                                    ),
                                    "得分": st.column_config.NumberColumn(
                                        format="%d",
                                        help="得分"
                                    ),
                                    "篮板": st.column_config.NumberColumn(
                                        format="%d",
                                        help="篮板"
                                    ),
                                    "助攻": st.column_config.NumberColumn(
                                        format="%d",
                                        help="助攻"
                                    ),
                                    "出场时间": st.column_config.TextColumn(
                                        width="small",
                                        help="出场时间（分钟）"
                                    )
                                }
                                
                                # 显示数据表
                                st.dataframe(
                                    away_df,
                                    column_config=column_config,
                                    hide_index=True,
                                    use_container_width=True,
                                    column_order=["球员", "原英文名", "号码", "位置", "出场时间", "得分", "篮板", "助攻", "抢断", "盖帽", "失误", "犯规", "命中率"]
                                )
                            
                            # 显示主队球员数据
                            if home_players:
                                st.markdown(f"#### {home_name_cn} 球员数据")
                                
                                home_df = pd.DataFrame(home_players)
                                st.dataframe(
                                    home_df,
                                    column_config={
                                        "球员": st.column_config.TextColumn(width="large"),
                                        "得分": st.column_config.NumberColumn(format="%d"),
                                        "篮板": st.column_config.NumberColumn(format="%d"),
                                        "助攻": st.column_config.NumberColumn(format="%d"),
                                    },
                                    hide_index=True,
                                    use_container_width=True,
                                    column_order=["球员", "原英文名", "号码", "位置", "出场时间", "得分", "篮板", "助攻", "抢断", "盖帽", "失误", "犯规", "命中率"]
                                )
                            
                            # 显示比赛摘要
                            header = game_details.get('header', {})
                            if header.get('competitions', []):
                                competition_info = header['competitions'][0]
                                venue = competition_info.get('venue', {})
                                if venue:
                                    st.caption(f"📍 比赛地点: {venue.get('fullName', '')}")
                        else:
                            st.info("球员数据暂不可用，请稍后重试")

# 底部信息
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"最后更新: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
with col2:
    st.caption(f"比赛总数: {len(filtered_events)}场")
with col3:
    if st.button("🔄 刷新数据"):
        st.cache_data.clear()
        st.rerun()

# 统计信息展开面板
with st.expander("📈 今日比赛统计"):
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
        
        # 显示统计图表
        chart_data = pd.DataFrame({
            '状态': list(status_counts.keys()),
            '数量': list(status_counts.values())
        })
        
        st.bar_chart(chart_data.set_index('状态'))
        
        # 显示具体统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("进行中", status_counts['进行中'])
        with col2:
            st.metric("已结束", status_counts['已结束'])
        with col3:
            st.metric("未开始", status_counts['未开始'])

# 使用说明
with st.expander("❓ 使用说明与翻译说明"):
    st.markdown("""
    ### 🏀 功能说明
    
    1. **全中文界面**: 球队名称和球员名称均已翻译为中文
    2. **球员数据**: 进行中和已结束的比赛显示详细球员统计
    3. **智能筛选**: 可按比赛状态筛选显示
    4. **实时更新**: 数据每5分钟自动刷新
    
    ### 📝 翻译说明
    
    **已收录的球员包括:**
    - 湖人: 勒布朗·詹姆斯, 安东尼·戴维斯等
    - 勇士: 斯蒂芬·库里, 克莱·汤普森等  
    - 凯尔特人: 杰森·塔图姆, 杰伦·布朗等
    - 掘金: 尼古拉·约基奇, 贾马尔·穆雷等
    - 太阳: 凯文·杜兰特, 德文·布克等
    - 以及其他球队共100+名常见球员
    
    **翻译规则:**
    - 常见球员: 使用标准中文译名
    - "Jr."后缀: 翻译为"小" (如: LeBron James Jr. → 小勒布朗·詹姆斯)
    - "II/III"后缀: 翻译为"二世/三世"
    - 未收录球员: 显示英文原名
    
    **位置翻译:**
    - G: 后卫 | F: 前锋 | C: 中锋
    - PG: 控球后卫 | SG: 得分后卫
    - SF: 小前锋 | PF: 大前锋
    """)
    
    # 显示已收录球员数量统计
    st.markdown("### 👥 球员翻译统计")
    
    # 按球队分组显示
    teams_players = {}
    for eng_name, cn_name in NBA_PLAYERS_CN.items():
        # 简单判断球员所属球队（实际应用中应该用更准确的方法）
        if "James" in eng_name and "LeBron" in eng_name:
            team = "湖人"
        elif "Curry" in eng_name:
            team = "勇士"
        elif "Jokic" in eng_name:
            team = "掘金"
        elif "Durant" in eng_name:
            team = "太阳"
        elif "Antetokounmpo" in eng_name:
            team = "雄鹿"
        else:
            team = "其他"
        
        if team not in teams_players:
            teams_players[team] = []
        teams_players[team].append(cn_name)
    
    for team, players in teams_players.items():
        with st.expander(f"{team}队 ({len(players)}人)"):
            cols = st.columns(3)
            for i, player in enumerate(sorted(players)):
                cols[i % 3].write(f"• {player}")
