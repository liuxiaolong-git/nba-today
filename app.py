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
        # 第一优先级：summary 接口（含 labels）
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # 如果有 boxscore 且 players 存在，直接返回
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return data
            else:
                # 尝试 fallback 到 boxscore
                pass
        else:
            # 失败则尝试 boxscore
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
        return f"{int(float(s))}:00"
    except:
        return s

def parse_player_stats(game_data):
    """使用 labels 或 boxscore 补全解析"""
    try:
        boxscore = game_data.get('boxscore', {})
        players = boxscore.get('players', [])
        away_data, home_data = [], []

        def extract_from_labels(team_section):
            stats_list = team_section.get('statistics', [])
            if not stats_list:
                return []
            main = stats_list[0]
            labels = main.get('labels', [])
            athletes = main.get('athletes', [])
            if not labels or not athletes:
                return []

            label_idx = {label: i for i, label in enumerate(labels)}
            result = []

            for ath in athletes:
                athlete = ath.get('athlete', {})
                stats = ath.get('stats', [])
                if not athlete or len(stats) <= max(label_idx.values()):
                    continue

                def g(label, default='0'):
                    i = label_idx.get(label)
                    if i is not None and 0 <= i < len(stats):
                        v = stats[i]
                        return str(v) if v not in ('', '--', 'N/A', None) else default
                    return default

                name = athlete.get('displayName', '').strip()
                if not name:
                    continue

                result.append({
                    '球员': name,
                    '时间': format_time(g('MIN')),
                    '得分': g('PTS'),
                    '投篮': f"{g('FGM')}/{g('FGA')}",
                    '三分': f"{g('3PM')}/{g('3PA')}",
                    '罚球': f"{g('FTM')}/{g('FTA')}",
                    '篮板': g('REB'),
                    '助攻': g('AST'),
                    '失误': g('TO')
                })
            return result

        def extract_from_boxscore(team_section):
            """从 boxscore 接口解析"""
            if not team_section:
                return []
            athletes = team_section.get('athletes', [])
            result = []
            for ath in athletes:
                player = ath.get('player', {})
                name = player.get('displayName', '').strip()
                if not name:
                    continue
                stats = player.get('statistics', [])
                fgm = next((s.get('value') for s in stats if s.get('name') == 'fieldGoalsMade'), '0')
                fga = next((s.get('value') for s in stats if s.get('name') == 'fieldGoalsAttempted'), '0')
                threepm = next((s.get('value') for s in stats if s.get('name') == 'threePointersMade'), '0')
                threepa = next((s.get('value') for s in stats if s.get('name') == 'threePointersAttempted'), '0')
                ftm = next((s.get('value') for s in stats if s.get('name') == 'freeThrowsMade'), '0')
                fta = next((s.get('value') for s in stats if s.get('name') == 'freeThrowsAttempt'), '0')
                pts = next((s.get('value') for s in stats if s.get('name') == 'points'), '0')
                reb = next((s.get('value') for s in stats if s.get('name') == 'rebounds'), '0')
                ast = next((s.get('value') for s in stats if s.get('name') == 'assists'), '0')
                tov = next((s.get('value') for s in stats if s.get('name') == 'turnovers'), '0')
                minutes = next((s.get('value') for s in stats if s.get('name') == 'minutes'), '0')

                result.append({
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
            return result

        # 先尝试 labels
        if len(players) > 0:
            away_data = extract_from_labels(players[0])
        if len(players) > 1:
            home_data = extract_from_labels(players[1])

        # 若仍为空，尝试 boxscore
        if not away_data and not home_data:
            # 重新请求 boxscore 数据
            boxscore_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/boxscore?event={game_data['id']}"
            try:
                box_resp = requests.get(boxscore_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                if box_resp.status_code == 200:
                    box_data = box_resp.json()
                    if box_data.get('teams'):
                        team_a = box_data['teams'][0].get('players', [])
                        team_b = box_data['teams'][1].get('players', [])
                        away_data = extract_from_boxscore(team_a)
                        home_data = extract_from_boxscore(team_b)
            except:
                pass

        return away_data, home_data

    except Exception as e:
        st.session_state.debug = str(e)
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

    # 时间
    try:
        utc_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
        bj_time = utc_time.astimezone(beijing_tz).strftime("%H:%M")
    except:
        bj_time = "时间待定"

    # 显示比赛
    cols = st.columns([2, 1, 0.5, 1, 2])
    cols[0].markdown(f"**{away_name}**")
    cols[1].markdown(f"**{away_score}**")
    cols[2].markdown("**VS**")
    cols[3].markdown(f"**{home_score}**")
    cols[4].markdown(f"**{home_name}**")
    st.caption(f"{badge} | {desc} | ⏰ {bj_time}")

    # 球员数据
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
                            df = df.sort_values
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

# Footer
st.divider()
col1, col2 = st.columns([3, 1])
col1.caption(f"更新于: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
if col2.button("🔄 刷新"):
    st.cache_data.clear()
    st.rerun()
