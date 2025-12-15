import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程")

if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

team_translation = {
    "Atlanta Hawks": "老鹰", "Boston Celtics": "凯尔特人", "Brooklyn Nets": "篮网",
    "Charlotte Hornets": "黄蜂", "Chicago Bulls": "公牛", "Cleveland Cavaliers": "骑士",
    "Dallas Mavericks": "独行侠", "Denver Nuggets": "掘金", "Detroit Pistons": "活塞",
    "Golden State Warriors": "勇士", "Houston Rockets": "火箭", "Indiana Pacers": "步行者",
    "LA Clippers": "快船", "Los Angeles Lakers": "湖人", "Memphis Grizzlies": "灰熊",
    "Miami Heat": "热火", "Milwaukee Bucks": "雄鹿", "Minnesota Timberwolves": "森林狼",
    "New Orleans Pelicans": "鹈鹕", "New York Knicks": "尼克斯", "Oklahoma City Thunder": "雷霆",
    "Orlando Magic": "魔术", "Philadelphia 76ers": "76人", "Phoenix Suns": "太阳",
    "Portland Trail Blazers": "开拓者", "Sacramento Kings": "国王", "San Antonio Spurs": "马刺",
    "Toronto Raptors": "猛龙", "Utah Jazz": "爵士", "Washington Wizards": "奇才"
}

def translate_team_name(name):
    return team_translation.get(name, name)

@st.cache_data(ttl=30)
def fetch_nba_schedule(date_str):
    try:
        eastern = pytz.timezone('America/New_York')
        beijing_dt = beijing_tz.localize(datetime.strptime(date_str, '%Y-%m-%d'))
        eastern_dt = beijing_dt.astimezone(eastern)
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        params = {'dates': eastern_dt.strftime('%Y%m%d'), 'lang': 'zh', 'region': 'cn'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"获取赛程失败: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_player_stats(event_id):
    """先尝试 summary，失败则用 boxscore 补全"""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return data
        # Fallback to boxscore
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/boxscore?event={event_id}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        st.session_state.debug = str(e)
        return None

def format_time(t):
    if not t or str(t).strip() in ('0', '0:00', '--', '', 'DNP', 'N/A'):
        return '0:00'
    s = str(t).strip()
    if ':' in s:
        return s
    try:
        minutes = int(float(s))
        return f"{minutes}:00"
    except:
        return s

def extract_stat_by_name(stats_list, stat_names):
    """从 stats list 中按多个可能的名字查找值"""
    for name in stat_names:
        for stat in stats_list:
            if stat.get('name') == name:
                return str(stat.get('value', '0'))
    return '0'

def parse_player_stats(game_data):
    try:
        # 获取主客场信息（用于 fallback）
        header = game_data.get('header', {})
        home_team_name = header.get('homeTeam', {}).get('displayName', '')
        away_team_name = header.get('awayTeam', {}).get('displayName', '')
        home_team_id = str(header.get('homeTeam', {}).get('id', '')).strip()
        away_team_id = str(header.get('awayTeam', {}).get('id', '')).strip()

        home_data, away_data = [], []

        players_section = game_data.get('boxscore', {}).get('players', [])
        if not players_section:
            return [], []

        for team_data in players_section:
            team_info = team_data.get('team', {})
            team_id = str(team_info.get('id', '')).strip()
            team_name = team_info.get('displayName', '').strip()
            stats_list = team_data.get('statistics', [])
            if not stats_list:
                continue
            main_stat = stats_list[0]
            labels = main_stat.get('labels', [])
            athletes = main_stat.get('athletes', [])
            
            parsed = []
            for ath in athletes:
                name = ath.get('athlete', {}).get('displayName', '').strip()
                raw_vals = ath.get('stats', [])
                if not name or not raw_vals:
                    continue

                stat_map = {}
                for i, label in enumerate(labels):
                    if i < len(raw_vals):
                        stat_map[label] = raw_vals[i]

                def parse_shot(s):
                    s = str(s).replace('/', '-').strip()
                    if '-' in s:
                        parts = s.split('-')
                        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                            return parts[0], parts[1]
                    return '0', '0'

                fgm, fga = parse_shot(stat_map.get('FGM-A', stat_map.get('FG', '0-0')))
                threepm, threepa = parse_shot(stat_map.get('3PM-A', stat_map.get('3PT', '0-0')))
                ftm, fta = parse_shot(stat_map.get('FTM-A', stat_map.get('FT', '0-0')))

                def get_num(key, default='0'):
                    val = stat_map.get(key, default)
                    return str(val) if str(val).replace('.', '').isdigit() else default

                minutes = stat_map.get('MIN', '0')
                pts = get_num('PTS')
                reb = get_num('REB')
                ast = get_num('AST')
                tov = get_num('TO')

                parsed.append({
                    '球员': name,
                    '时间': format_time(minutes),
                    '得分': pts,
                    '投篮': f"{fgm}/{fga}",
                    '三分': f"{threepm}/{threepa}",
                    '罚球': f"{ftm}/{fta}",
                    '篮板': reb,
                    '助攻': ast,
                    '失误': tov
                })

            # ✅ 第一优先级：用 ID 匹配
            assigned = False
            if team_id == away_team_id:
                away_data = parsed
                assigned = True
            elif team_id == home_team_id:
                home_data = parsed
                assigned = True

            # ✅ 第二优先级：ID 失败？用名称匹配（模糊）
            if not assigned:
                if away_team_name and away_team_name in team_name or team_name in away_team_name:
                    away_data = parsed
                elif home_team_name and home_team_name in team_name or team_name in home_team_name:
                    home_data = parsed

        return away_data, home_data
    except Exception as e:
        st.session_state.debug = f"Parse error: {str(e)}"
        return [], []
# Sidebar
with st.sidebar:
    st.header("⚙️ 查询设置")
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3)
    )

# Main
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

with st.spinner("加载赛程..."):
    schedule = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule or 'events' not in schedule:
    st.error("无法获取数据")
    st.stop()

events = schedule['events']
if not events:
    st.info("今日无比赛")
    st.stop()

for i, event in enumerate(events):
    comp = event.get('competitions', [{}])[0]
    competitors = comp.get('competitors', [])
    if len(competitors) < 2:
        continue

    away = competitors[0]
    home = competitors[1]
    away_name = translate_team_name(away.get('team', {}).get('displayName', '客队'))
    home_name = translate_team_name(home.get('team', {}).get('displayName', '主队'))
    away_score = away.get('score', '0')
    home_score = home.get('score', '0')

    status_type = event.get('status', {}).get('type', {})
    state = status_type.get('state', 'pre')
    desc = status_type.get('description', '未开始')
    badge = {"in": "🟢 进行中", "post": "⚫ 已结束"}.get(state, "⏳ 未开始")

    try:
        utc_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
        bj_time = utc_time.astimezone(beijing_tz).strftime("%H:%M")
    except:
        bj_time = "时间待定"

    cols = st.columns([2, 1, 0.5, 1, 2])
    cols[0].markdown(f"**{away_name}**")
    cols[1].markdown(f"**{away_score}**")
    cols[2].markdown("**VS**")
    cols[3].markdown(f"**{home_score}**")
    cols[4].markdown(f"**{home_name}**")
    st.caption(f"{badge} | {desc} | ⏰ {bj_time}")

    if state in ['in', 'post']:
        with st.spinner("加载球员数据..."):
            game_data = fetch_player_stats(event['id'])
            if game_data:
                away_p, home_p = parse_player_stats(game_data)
                if away_p or home_p:
                    st.subheader("📊 球员数据")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**{away_name}**")
                        if away_p:
                            df = pd.DataFrame(away_p)
                            df['pts'] = pd.to_numeric(df['得分'], errors='coerce')
                            df = df.sort_values('pts', ascending=False).drop('pts', axis=1)
                            st.dataframe(df, hide_index=True, use_container_width=True)
                        else:
                            st.info("无数据")
                    with c2:
                        st.markdown(f"**{home_name}**")
                        if home_p:
                            df = pd.DataFrame(home_p)
                            df['pts'] = pd.to_numeric(df['得分'], errors='coerce')
                            df = df.sort_values('pts', ascending=False).drop('pts', axis=1)
                            st.dataframe(df, hide_index=True, use_container_width=True)
                        else:
                            st.info("无数据")
            else:
                st.warning("球员数据加载失败")

    if i < len(events) - 1:
        st.divider()

st.divider()
col1, col2 = st.columns([3, 1])
col1.caption(f"更新于: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
if col2.button("🔄 刷新"):
    st.cache_data.clear()
    st.rerun()





