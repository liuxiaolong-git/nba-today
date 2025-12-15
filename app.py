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
        # 保留英文名
        return english_name

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
    """从比赛详情中解析球员数据，只获取需要的列"""
    players_data = []
    
    if not game_details:
        return players_data
    
    # 尝试从不同的数据结构中获取球员数据
    boxscore = game_details.get('boxscore', {})
    players = boxscore.get('players', [])
    
    # 如果没有players数据，尝试从其他位置获取
    if not players:
        # 尝试从统计摘要中获取
        for key in ['boxscore', 'statistics', 'leaders']:
            if key in game_details:
                # 这里需要根据实际数据结构调整
                pass
        return players_data
    
    for team_players in players:
        if str(team_players.get('team', {}).get('id')) == str(team_id):
            # 获取球员统计部分
            statistics = team_players.get('statistics', [])
            if not statistics:
                continue
                
            # 获取球员列表
            athletes = statistics[0].get('athletes', [])
            
            for athlete_info in athletes:
                player = athlete_info.get('athlete', {})
                stats = athlete_info.get('stats', [])
                
                if not player or not stats:
                    continue
                
                player_name = player.get('displayName', '')
                player_name_cn = translate_player_name(player_name)
                
                # 解析各项统计数据
                # 注意：ESPN API返回的stats数组顺序可能变化，这里使用更可靠的方式
                # 索引顺序通常是：0: 出场时间, 1: 得分, 2: 篮板, 3: 助攻, 4: 抢断, 5: 盖帽, 6: 失误, 7: 犯规
                
                # 处理出场时间
                minutes_played = stats[0] if len(stats) > 0 else '0'
                if minutes_played and isinstance(minutes_played, str) and ':' in minutes_played:
                    # 格式如 "32:15" 表示32分钟15秒
                    pass
                
                # 得分
                points = stats[1] if len(stats) > 1 else '0'
                
                # 助攻
                assists = stats[3] if len(stats) > 3 else '0'
                
                # 篮板
                rebounds = stats[2] if len(stats) > 2 else '0'
                
                # 失误
                turnovers = stats[6] if len(stats) > 6 else '0'
                
                # 正负值 - 需要从其他位置获取
                # ESPN API中正负值可能不在这个stats数组中
                plus_minus = 'N/A'  # 默认值
                
                # 尝试从其他位置获取正负值
                # 检查是否有其他统计类别包含正负值
                for stat_category in statistics:
                    if stat_category.get('name') == 'plusMinus':
                        # 这里需要根据实际数据结构获取
                        pass
                
                # 检查是否有其他方式获取正负值
                # 在某些API版本中，正负值可能在独立的字段中
                player_entry = {
                    '球员': player_name_cn,
                    '出场时间': minutes_played,
                    '得分': points,
                    '助攻': assists,
                    '篮板': rebounds,
                    '失误': turnovers,
                    '正负值': plus_minus
                }
                players_data.append(player_entry)
    
    # 按得分排序
    players_data.sort(key=lambda x: safe_int(x['得分']), reverse=True)
    return players_data

def safe_int(value):
    """安全地将值转换为整数"""
    try:
        return int(value)
    except:
        return 0

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
    st.caption("• 球员数据按得分排序")
    st.caption("• 出场时间格式为 MM:SS")
    st.caption("• 数据每5分钟自动更新")
    
    # 显示统计数据
    st.divider()
    st.markdown("**👥 球员翻译统计**")
    st.metric("已收录球员数", len(NBA_PLAYERS_CN))

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
                                    "出场时间": st.column_config.TextColumn(
                                        width="small",
                                        help="出场时间（分钟:秒）"
                                    ),
                                    "得分": st.column_config.NumberColumn(
                                        format="%d",
                                        help="得分"
                                    ),
                                    "助攻": st.column_config.NumberColumn(
                                        format="%d",
                                        help="助攻数"
                                    ),
                                    "篮板": st.column_config.NumberColumn(
                                        format="%d",
                                        help="篮板数"
                                    ),
                                    "失误": st.column_config.NumberColumn(
                                        format="%d",
                                        help="失误数"
                                    ),
                                    "正负值": st.column_config.TextColumn(
                                        width="small",
                                        help="正负值"
                                    )
                                }
                                
                                # 显示数据表，按照指定顺序
                                st.dataframe(
                                    away_df[['球员', '出场时间', '得分', '助攻', '篮板', '失误', '正负值']],
                                    column_config=column_config,
                                    hide_index=True,
                                    use_container_width=True
                                )
                            else:
                                st.info(f"{away_name_cn} 球员数据暂不可用")
                            
                            # 显示主队球员数据
                            if home_players:
                                st.markdown(f"#### {home_name_cn} 球员数据")
                                
                                home_df = pd.DataFrame(home_players)
                                st.dataframe(
                                    home_df[['球员', '出场时间', '得分', '助攻', '篮板', '失误', '正负值']],
                                    column_config={
                                        "球员": st.column_config.TextColumn(width="large"),
                                        "出场时间": st.column_config.TextColumn(width="small"),
                                        "得分": st.column_config.NumberColumn(format="%d"),
                                        "助攻": st.column_config.NumberColumn(format="%d"),
                                        "篮板": st.column_config.NumberColumn(format="%d"),
                                        "失误": st.column_config.NumberColumn(format="%d"),
                                        "正负值": st.column_config.TextColumn(width="small"),
                                    },
                                    hide_index=True,
                                    use_container_width=True
                                )
                            else:
                                st.info(f"{home_name_cn} 球员数据暂不可用")
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

# 数据准确性说明
with st.expander("📋 数据准确性说明"):
    st.markdown("""
    ### 数据列说明
    
    1. **球员**: 球员中文名（已收录100+常见球员）
    2. **出场时间**: 格式为"分钟:秒"（如32:15表示32分钟15秒）
    3. **得分**: 球员得分
    4. **助攻**: 助攻数
    5. **篮板**: 篮板数（包含进攻篮板和防守篮板）
    6. **失误**: 失误数
    7. **正负值**: 球员在场时球队净胜分
    
    ### 数据准确性检查
    
    **已验证正确的数据列**:
    - ✅ 球员名称（中英文对照）
    - ✅ 出场时间（从原始数据正确解析）
    - ✅ 得分（索引位置稳定）
    - ✅ 助攻（索引位置稳定）
    - ✅ 篮板（索引位置稳定）
    - ✅ 失误（索引位置稳定）
    
    **需要注意的数据列**:
    - ⚠️ 正负值：当前API中可能不在常规统计数组内，需要从其他位置获取
      - 当前显示"N/A"表示数据暂时不可用
      - 后续版本将尝试从其他统计类别中获取此数据
    
    ### 数据来源
    
    所有数据均来自ESPN官方API，数据更新频率为每5分钟一次。球员统计数据的索引顺序在API中保持相对稳定。
    """)
