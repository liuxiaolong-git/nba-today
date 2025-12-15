import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import concurrent.futures

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程")
st.caption("数据来源: ESPN公开接口 | 全中文")

# 初始化会话状态
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# 球队名称翻译字典
team_translation = {
    "Atlanta Hawks": "亚特兰大老鹰队",
    "Boston Celtics": "波士顿凯尔特人队", 
    "Brooklyn Nets": "布鲁克林篮网队",
    "Charlotte Hornets": "夏洛特黄蜂队",
    "Chicago Bulls": "芝加哥公牛队",
    "Cleveland Cavaliers": "克里夫兰骑士队",
    "Dallas Mavericks": "达拉斯独行侠队",
    "Denver Nuggets": "丹佛掘金队",
    "Detroit Pistons": "底特律活塞队",
    "Golden State Warriors": "金州勇士队",
    "Houston Rockets": "休斯顿火箭队",
    "Indiana Pacers": "印第安纳步行者队",
    "LA Clippers": "洛杉矶快船队",
    "Los Angeles Clippers": "洛杉矶快船队",
    "Los Angeles Lakers": "洛杉矶湖人队",
    "Memphis Grizzlies": "孟菲斯灰熊队",
    "Miami Heat": "迈阿密热火队",
    "Milwaukee Bucks": "密尔沃基雄鹿队",
    "Minnesota Timberwolves": "明尼苏达森林狼队",
    "New Orleans Pelicans": "新奥尔良鹈鹕队",
    "New York Knicks": "纽约尼克斯队",
    "Oklahoma City Thunder": "俄克拉荷马城雷霆队",
    "Orlando Magic": "奥兰多魔术队",
    "Philadelphia 76ers": "费城76人队",
    "Phoenix Suns": "菲尼克斯太阳队",
    "Portland Trail Blazers": "波特兰开拓者队",
    "Sacramento Kings": "萨克拉门托国王队",
    "San Antonio Spurs": "圣安东尼奥马刺队",
    "Toronto Raptors": "多伦多猛龙队",
    "Utah Jazz": "犹他爵士队",
    "Washington Wizards": "华盛顿奇才队",
    "Team LeBron": "勒布朗队",
    "Team Giannis": "字母哥队",
    "Team Durant": "杜兰特队"
}

def translate_team_name(team_name_en):
    """翻译球队名称"""
    return team_translation.get(team_name_en, team_name_en)

@st.cache_data(ttl=30, show_spinner=False)
def fetch_nba_schedule(date_str):
    """获取NBA赛程数据 - 优化版"""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        params = {
            'dates': date_str.replace('-', ''),
            'lang': 'zh',
            'region': 'cn'
        }

        # 设置更短的超时时间
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        st.error("请求超时，请稍后重试")
        return None
    except Exception as e:
        st.error(f"获取赛程失败: {str(e)}")
        return None

def fetch_player_stats_parallel(event_id, competitors):
    """并行获取球员统计数据"""
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        params = {'event': event_id}
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return extract_player_stats(data, competitors)
    except:
        pass
    return [], []

def extract_player_stats(game_data, competitors):
    """从比赛摘要数据中提取球员统计"""
    try:
        boxscore = game_data.get('boxscore', {})
        players = boxscore.get('players', [])
        
        if not players or len(players) < 2:
            return [], []
        
        away_players_data = []
        home_players_data = []
        
        # 处理客队球员
        for player in players[0].get('statistics', [{}])[0].get('athletes', []):
            athlete = player.get('athlete', {})
            stats = player.get('stats', [])
            if athlete and stats:
                player_info = {
                    '球员': athlete.get('displayName', ''),
                    '出场时间': format_time(stats[0]) if len(stats) > 0 else '0:00',
                    '得分': str(stats[1]) if len(stats) > 1 else '0',
                    '投篮': f"{stats[2]}-{stats[3]}" if len(stats) > 3 else '0-0',
                    '三分': f"{stats[4]}-{stats[5]}" if len(stats) > 5 else '0-0',
                    '助攻': str(stats[7]) if len(stats) > 7 else '0',
                    '篮板': str(stats[6]) if len(stats) > 6 else '0',
                    '失误': str(stats[9]) if len(stats) > 9 else '0',
                }
                away_players_data.append(player_info)
        
        # 处理主队球员
        for player in players[1].get('statistics', [{}])[0].get('athletes', []):
            athlete = player.get('athlete', {})
            stats = player.get('stats', [])
            if athlete and stats:
                player_info = {
                    '球员': athlete.get('displayName', ''),
                    '出场时间': format_time(stats[0]) if len(stats) > 0 else '0:00',
                    '得分': str(stats[1]) if len(stats) > 1 else '0',
                    '投篮': f"{stats[2]}-{stats[3]}" if len(stats) > 3 else '0-0',
                    '三分': f"{stats[4]}-{stats[5]}" if len(stats) > 5 else '0-0',
                    '助攻': str(stats[7]) if len(stats) > 7 else '0',
                    '篮板': str(stats[6]) if len(stats) > 6 else '0',
                    '失误': str(stats[9]) if len(stats) > 9 else '0',
                }
                home_players_data.append(player_info)
        
        return away_players_data, home_players_data
    except Exception as e:
        return [], []

def format_time(time_str):
    """格式化时间显示"""
    if not time_str:
        return '0:00'
    if ':' in time_str:
        return time_str
    try:
        minutes = int(time_str)
        return f"{minutes}:00" if minutes < 10 else f"{minutes}:00"
    except:
        return time_str

def display_player_stats_tab(away_players, home_players, away_name, home_name):
    """显示球员数据标签页"""
    tab1, tab2 = st.tabs([f"{away_name}", f"{home_name}"])
    
    with tab1:
        if away_players:
            away_df = pd.DataFrame(away_players)
            if '得分' in away_df.columns:
                away_df['得分_int'] = pd.to_numeric(away_df['得分'], errors='coerce')
                away_df = away_df.sort_values('得分_int', ascending=False).drop('得分_int', axis=1)
            st.dataframe(
                away_df,
                hide_index=True,
                use_container_width=True,
                height=min(400, len(away_players) * 35 + 50)
            )
        else:
            st.info("暂无球员数据")
    
    with tab2:
        if home_players:
            home_df = pd.DataFrame(home_players)
            if '得分' in home_df.columns:
                home_df['得分_int'] = pd.to_numeric(home_df['得分'], errors='coerce')
                home_df = home_df.sort_values('得分_int', ascending=False).drop('得分_int', axis=1)
            st.dataframe(
                home_df,
                hide_index=True,
                use_container_width=True,
                height=min(400, len(home_players) * 35 + 50)
            )
        else:
            st.info("暂无球员数据")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 查询设置")
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3)
    )
    
    # 添加刷新按钮
    if st.button("🔄 立即刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.rerun()

# 主界面
st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')} NBA赛程")

# 使用容器预加载
with st.container():
    # 获取赛程数据
    schedule_data = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule_data:
    st.warning("无法获取赛程数据，请检查网络连接或稍后重试。")
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
    if not competitions:
        continue
        
    competition = competitions[0]
    competitors = competition.get('competitors', [])
    
    if len(competitors) < 2:
        continue
    
    away_team = competitors[0].get('team', {})
    home_team = competitors[1].get('team', {})
    
    away_name_en = away_team.get('displayName', '')
    home_name_en = home_team.get('displayName', '')
    
    away_name_cn = translate_team_name(away_name_en)
    home_name_cn = translate_team_name(home_name_en)
    
    away_score = competitors[0].get('score', '0')
    home_score = competitors[1].get('score', '0')
    
    # 创建比赛卡片
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 3])
        
        with col1:
            st.markdown(f"### {away_name_cn}")
            st.markdown(f"**{away_score}**")
            
        with col2:
            st.markdown("## VS")
            st.markdown(f"*{status_badge}*")
            st.markdown(f"**{game_time}**")
            
        with col3:
            st.markdown(f"### {home_name_cn}")
            st.markdown(f"**{home_score}**")
        
        # 比赛详情展开
        with st.expander("查看比赛详情", expanded=False):
            # 如果比赛已结束或进行中，显示球员数据
            if status_detail in ['in', 'post']:
                # 使用会话状态缓存球员数据
                cache_key = f"player_stats_{event_id}"
                if cache_key not in st.session_state:
                    # 并行获取球员数据
                    with st.spinner(f"正在加载{away_name_cn} vs {home_name_cn}的球员数据..."):
                        away_players, home_players = fetch_player_stats_parallel(event_id, competitors)
                        st.session_state[cache_key] = (away_players, home_players)
                
                away_players, home_players = st.session_state[cache_key]
                
                if away_players or home_players:
                    display_player_stats_tab(away_players, home_players, away_name_cn, home_name_cn)
                else:
                    st.info("球员数据暂不可用")
            
            # 显示比赛其他信息
            venue = competition.get('venue', {}).get('fullName', '')
            if venue:
                st.caption(f"🏟️ 比赛地点: {venue}")
            
            # 显示比赛进程（如果有）
            if status_detail == 'in':
                try:
                    broadcasts = competition.get('broadcasts', [])
                    if broadcasts:
                        broadcast_names = [b.get('names', [])[0] for b in broadcasts if b.get('names')]
                        if broadcast_names:
                            st.caption(f"📺 直播: {', '.join(broadcast_names)}")
                except:
                    pass
    
    # 比赛之间的分隔线
    if i < len(events) - 1:
        st.divider()

# 底部状态栏
st.divider()
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.caption(f"最后更新: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
with col2:
    st.caption(f"比赛数量: {len(events)}")
with col3:
    if st.button("🔄 刷新页面", key="bottom_refresh"):
        st.cache_data.clear()
        st.rerun()

# 添加CSS样式优化
st.markdown("""
<style>
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)
