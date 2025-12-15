import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程与球员数据")
st.caption("数据来源: ESPN公开接口 | 完全免费 | 实时更新")

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)
today_str = now_beijing.strftime('%Y-%m-%d')

# NBA球队中英文对照表
NBA_TEAMS_CN = {
    # 东部联盟
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
    
    # 西部联盟
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
    "Utah Jazz": "犹他爵士",
    
    # 备用名称
    "Lakers": "洛杉矶湖人",
    "Warriors": "金州勇士",
    "Celtics": "波士顿凯尔特人",
    "Nets": "布鲁克林篮网",
    "Bucks": "密尔沃基雄鹿",
    "Suns": "菲尼克斯太阳",
    "Heat": "迈阿密热火",
    "76ers": "费城76人",
    "Nuggets": "丹佛掘金",
    "Grizzlies": "孟菲斯灰熊",
    "Kings": "萨克拉门托国王",
    "Cavaliers": "克里夫兰骑士",
    "Knicks": "纽约尼克斯",
    "Clippers": "洛杉矶快船",
    "Mavericks": "达拉斯独行侠",
    "Timberwolves": "明尼苏达森林狼",
    "Thunder": "俄克拉荷马雷霆",
    "Pelicans": "新奥尔良鹈鹕",
    "Hawks": "亚特兰大老鹰",
    "Bulls": "芝加哥公牛",
    "Pacers": "印第安纳步行者",
    "Wizards": "华盛顿奇才",
    "Magic": "奥兰多魔术",
    "Rockets": "休斯顿火箭",
    "Spurs": "圣安东尼奥马刺",
    "Trail Blazers": "波特兰开拓者",
    "Hornets": "夏洛特黄蜂",
    "Pistons": "底特律活塞",
    "Jazz": "犹他爵士",
    "Raptors": "多伦多猛龙"
}

def translate_team_name(english_name):
    """将英文队名转换为中文"""
    return NBA_TEAMS_CN.get(english_name, english_name)

@st.cache_data(ttl=300)  # 缓存5分钟
def fetch_nba_schedule(date_str):
    """获取NBA赛程数据"""
    try:
        # 将北京时间转换为美东时间
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

@st.cache_data(ttl=180)  # 缓存3分钟（球员数据更新更频繁）
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
    
    # 查找球员统计部分
    boxscore = game_details.get('boxscore', {})
    players = boxscore.get('players', [])
    
    for team_players in players:
        if team_players.get('team', {}).get('id') == str(team_id):
            for player_info in team_players.get('statistics', [])[0].get('athletes', []):
                player = player_info.get('athlete', {})
                stats = player_info.get('stats', [])
                
                if player and stats:
                    player_entry = {
                        '球员': player.get('displayName', ''),
                        '号码': player.get('jersey', ''),
                        '位置': player.get('position', {}).get('abbreviation', ''),
                        '出场时间': stats[0] if len(stats) > 0 else '0',
                        '得分': stats[1] if len(stats) > 1 else '0',
                        '篮板': stats[2] if len(stats) > 2 else '0',
                        '助攻': stats[3] if len(stats) > 3 else '0',
                        '抢断': stats[4] if len(stats) > 4 else '0',
                        '盖帽': stats[5] if len(stats) > 5 else '0',
                        '失误': stats[6] if len(stats) > 6 else '0',
                        '犯规': stats[7] if len(stats) > 7 else '0',
                        '命中率': f"{stats[8]}%" if len(stats) > 8 and stats[8] else '0%'
                    }
                    players_data.append(player_entry)
    
    return players_data

# 侧边栏：日期选择和筛选
with st.sidebar:
    st.header("⚙️ 查询设置")
    
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=30),
        max_value=now_beijing.date() + timedelta(days=30)
    )
    
    show_all = st.checkbox("显示所有比赛", value=True)
    if not show_all:
        status_filter = st.multiselect(
            "比赛状态筛选",
            options=["未开始", "进行中", "已结束"],
            default=["进行中", "已结束"]
        )
    
    st.divider()
    st.markdown("**💡 功能说明**")
    st.caption("• 点击比赛卡片查看球员数据")
    st.caption("• 进行中和已结束的比赛可查看详细统计")
    st.caption("• 数据每5分钟自动更新")

# 主内容区
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')} 赛程")
    
    # 获取数据
    with st.spinner("正在获取NBA赛程数据..."):
        schedule_data = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))
    
    if not schedule_data:
        st.error("无法获取赛程数据，请检查网络连接或稍后重试")
        st.stop()
    
    events = schedule_data.get('events', [])
    
    if not events:
        st.info("今日暂无NBA比赛安排")
        
        # 尝试查找最近有比赛的日期
        st.write("尝试查找最近的比赛...")
        for i in range(1, 4):
            check_date = (selected_date + timedelta(days=i)).strftime('%Y-%m-%d')
            future_data = fetch_nba_schedule(check_date)
            if future_data and future_data.get('events'):
                st.success(f"发现 {check_date} 有比赛安排")
                if st.button(f"查看 {check_date} 的赛程"):
                    selected_date = datetime.strptime(check_date, '%Y-%m-%d').date()
                    st.experimental_rerun()
                break
        st.stop()
    
    # 显示比赛列表
    for event in events:
        # 比赛基本信息
        event_id = event.get('id', '')
        name = event.get('name', 'NBA比赛')
        
        # 比赛状态
        status = event.get('status', {})
        status_type = status.get('type', {}).get('description', '未开始')
        status_detail = status.get('type', {}).get('state', 'pre')
        
        # 确定状态颜色和文本
        if status_detail == 'in':
            status_text = "🟢 进行中"
            status_color = "green"
            show_details = True
        elif status_detail == 'post':
            status_text = "⚫ 已结束"
            status_color = "gray"
            show_details = True
        else:
            status_text = "⏳ 未开始"
            status_color = "blue"
            show_details = False
        
        # 检查是否需要根据筛选显示
        status_mapping = {
            'pre': '未开始',
            'in': '进行中',
            'post': '已结束'
        }
        current_status = status_mapping.get(status_detail, '未开始')
        
        if not show_all and current_status not in status_filter:
            continue
        
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
                
                # 显示比赛卡片
                with st.expander(f"{status_text} | {away_name_cn} vs {home_name_cn}", expanded=show_details):
                    # 比分展示
                    col_a, col_vs, col_h = st.columns([2, 1, 2])
                    
                    with col_a:
                        st.markdown(f"### 🏀 {away_name_cn}")
                        st.markdown(f"**{away_score}**")
                    
                    with col_vs:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("**VS**")
                        st.markdown(f"*{game_time}*")
                    
                    with col_h:
                        st.markdown(f"### 🏠 {home_name_cn}")
                        st.markdown(f"**{home_score}**")
                    
                    # 显示比赛详情
                    st.caption(f"比赛时间: {game_date} {game_time} | 状态: {status_type}")
                    
                    # 比赛链接
                    links = event.get('links', [])
                    for link in links[:2]:
                        if 'href' in link:
                            st.markdown(f"[📺 {link.get('text', '观看直播')}]({link['href']})")
                    
                    # 如果是进行中或已结束的比赛，显示球员数据
                    if show_details and event_id:
                        with st.spinner("正在获取球员数据..."):
                            game_details = fetch_game_details(event_id)
                            
                            if game_details:
                                st.markdown("### 📊 球员数据统计")
                                
                                # 获取球员数据
                                away_players = parse_player_stats(game_details, away_id)
                                home_players = parse_player_stats(game_details, home_id)
                                
                                if away_players:
                                    st.markdown(f"**{away_name_cn} 球员数据**")
                                    away_df = pd.DataFrame(away_players)
                                    st.dataframe(
                                        away_df,
                                        column_config={
                                            "球员": st.column_config.TextColumn(width="large"),
                                            "得分": st.column_config.NumberColumn(format="%d"),
                                            "篮板": st.column_config.NumberColumn(format="%d"),
                                            "助攻": st.column_config.NumberColumn(format="%d"),
                                        },
                                        hide_index=True,
                                        use_container_width=True
                                    )
                                
                                if home_players:
                                    st.markdown(f"**{home_name_cn} 球员数据**")
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
                                        use_container_width=True
                                    )
                                
                                # 显示比赛摘要（如果有）
                                header = game_details.get('header', {})
                                if header.get('competitions', []):
                                    competition_info = header['competitions'][0]
                                    venue = competition_info.get('venue', {})
                                    if venue:
                                        st.caption(f"📍 比赛地点: {venue.get('fullName', '')}")
                                    
                                    # 显示比赛进程（如果有）
                                    play_by_play = game_details.get('plays', [])
                                    if play_by_play:
                                        st.markdown("#### 📝 比赛关键时刻")
                                        for i, play in enumerate(play_by_play[-5:]):  # 显示最近5个事件
                                            text = play.get('text', '')
                                            if text:
                                                st.write(f"• {text}")
                            else:
                                st.info("球员数据暂不可用")

with col2:
    st.subheader("📈 今日亮点")
    
    if events:
        # 统计比赛状态
        status_count = {'进行中': 0, '已结束': 0, '未开始': 0}
        for event in events:
            status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
            if status_detail == 'in':
                status_count['进行中'] += 1
            elif status_detail == 'post':
                status_count['已结束'] += 1
            else:
                status_count['未开始'] += 1
        
        # 显示统计信息
        st.metric("总比赛场次", len(events))
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("进行中", status_count['进行中'], delta=status_count['进行中'])
        with col_stat2:
            st.metric("已结束", status_count['已结束'])
        
        # 显示正在进行的高分比赛
        st.markdown("#### 🔥 高分对决")
        high_score_games = []
        for event in events:
            competitions = event.get('competitions', [])
            if competitions:
                competitors = competitions[0].get('competitors', [])
                if len(competitors) >= 2:
                    away_score = int(competitors[0].get('score', '0'))
                    home_score = int(competitors[1].get('score', '0'))
                    total_score = away_score + home_score
                    
                    status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
                    if status_detail == 'in' and total_score > 200:
                        away_team = translate_team_name(competitors[0].get('team', {}).get('displayName', ''))
                        home_team = translate_team_name(competitors[1].get('team', {}).get('displayName', ''))
                        high_score_games.append({
                            '比赛': f"{away_team} vs {home_team}",
                            '比分': f"{away_score} - {home_score}",
                            '总分': total_score
                        })
        
        if high_score_games:
            for game in high_score_games:
                st.info(f"**{game['比赛']}**\n\n比分: {game['比分']} (总分: {game['总分']})")
        else:
            st.info("暂无高分比赛")
        
        # 即将开始的比赛
        st.markdown("#### ⏰ 即将开始")
        upcoming_games = []
        for event in events:
            status_detail = event.get('status', {}).get('type', {}).get('state', 'pre')
            if status_detail == 'pre':
                competitions = event.get('competitions', [])
                if competitions:
                    competitors = competitions[0].get('competitors', [])
                    if len(competitors) >= 2:
                        away_team = translate_team_name(competitors[0].get('team', {}).get('displayName', ''))
                        home_team = translate_team_name(competitors[1].get('team', {}).get('displayName', ''))
                        
                        date_str = event.get('date', '')
                        if date_str:
                            try:
                                utc_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                beijing_time = utc_time.astimezone(beijing_tz)
                                game_time = beijing_time.strftime("%H:%M")
                                upcoming_games.append(f"{game_time} {away_team} vs {home_team}")
                            except:
                                upcoming_games.append(f"时间待定 {away_team} vs {home_team}")
        
        if upcoming_games:
            for game in upcoming_games[:3]:  # 只显示最近3场
                st.write(f"• {game}")
        else:
            st.info("今日无即将开始的比赛")

# 底部信息
st.divider()
st.caption(f"最后更新: {datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')} | 数据每5分钟自动刷新")
st.caption("💡 提示: 球员数据只在比赛开始后才会显示，未开始的比赛需要等待比赛开始")

# 添加自动刷新
if st.button("🔄 手动刷新数据"):
    st.cache_data.clear()
    st.experimental_rerun()

# 添加说明
with st.expander("❓ 使用说明"):
    st.markdown("""
    ### 功能说明
    
    1. **球队名称**: 已自动转换为中文名称，方便国内用户查看
    2. **球员数据**: 
       - 进行中和已结束的比赛会自动显示球员详细数据
       - 包括得分、篮板、助攻、抢断、盖帽等关键统计
       - 数据会随着比赛进展实时更新
    
    3. **状态说明**:
       - 🟢 进行中: 比赛正在进行，可以查看实时数据和球员统计
       - ⚫ 已结束: 比赛已结束，可以查看最终数据和球员统计
       - ⏳ 未开始: 比赛尚未开始，球员数据在比赛开始后才会显示
    
    4. **侧边栏功能**:
       - 可以查询任意日期的比赛
       - 可以按比赛状态筛选
       - 右侧面板显示今日比赛亮点和统计
    
    5. **数据更新**:
       - 赛程数据每5分钟自动更新
       - 球员数据每3分钟更新一次
       - 可以点击"手动刷新数据"按钮强制更新
    """)
