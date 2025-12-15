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

# ====== 球队中英文映射 ======
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

# ====== 球员中英文映射（高频球员）======
player_translation = {
    # 湖人
    "LeBron James": "勒布朗·詹姆斯",
    "Anthony Davis": "安东尼·戴维斯",
    "Austin Reaves": "奥斯汀·里夫斯",
    "D'Angelo Russell": "丹吉洛·拉塞尔",
    "Rui Hachimura": "八村垒",
    "Jarred Vanderbilt": "贾里德·范德比尔特",
    "Gabe Vincent": "加布·文森特",
    "Christian Wood": "克里斯蒂安·伍德",
    # 勇士
    "Stephen Curry": "斯蒂芬·库里",
    "Klay Thompson": "克莱·汤普森",
    "Draymond Green": "德雷蒙德·格林",
    "Andrew Wiggins": "安德鲁·威金斯",
    "Chris Paul": "克里斯·保罗",
    "Gary Payton II": "小加里·佩顿",
    "Moses Moody": "摩西·穆迪",
    "Brandin Podziemski": "布兰丁·波杰姆斯基",
    # 凯尔特人
    "Jayson Tatum": "杰森·塔图姆",
    "Jaylen Brown": "杰伦·布朗",
    "Kristaps Porzingis": "克里斯塔普斯·波尔津吉斯",
    "Jrue Holiday": "朱·霍勒迪",
    "Derrick White": "德里克·怀特",
    "Al Horford": "艾尔·霍福德",
    # 掘金
    "Nikola Jokic": "尼古拉·约基奇",
    "Jamal Murray": "贾马尔·穆雷",
    "Michael Porter Jr.": "小迈克尔·波特",
    "Aaron Gordon": "阿隆·戈登",
    "Kentavious Caldwell-Pope": "肯塔维奥斯·考德威尔-波普",
    # 独行侠
    "Luka Doncic": "卢卡·东契奇",
    "Kyrie Irving": "凯里·欧文",
    "P.J. Washington": "P.J. 华盛顿",
    "Daniel Gafford": "丹尼尔·加福德",
    "Derrick Jones Jr.": "小德里克·琼斯",
    # 雄鹿
    "Giannis Antetokounmpo": "扬尼斯·阿德托昆博",
    "Damian Lillard": "达米安·利拉德",
    "Brook Lopez": "布鲁克·洛佩斯",
    "Bobby Portis": "鲍比·波蒂斯",
    # 其他明星
    "Kevin Durant": "凯文·杜兰特",
    "Devin Booker": "德文·布克",
    "Joel Embiid": "乔尔·恩比德",
    "Tyrese Maxey": "泰瑞斯·马克西",
    "Shai Gilgeous-Alexander": "谢伊·吉尔杰斯-亚历山大",
    "Paul George": "保罗·乔治",
    "James Harden": "詹姆斯·哈登",
    "Kawhi Leonard": "科怀·伦纳德",
    "Zion Williamson": "锡安·威廉森",
    "Brandon Ingram": "布兰登·英格拉姆",
    "Trae Young": "特雷·杨",
    "De'Aaron Fox": "德阿龙·福克斯",
    "Domantas Sabonis": "多曼塔斯·萨博尼斯",
    "Ja Morant": "贾·莫兰特",
    "Jaren Jackson Jr.": "小贾伦·杰克逊",
    "Donovan Mitchell": "多诺万·米切尔",
    "Evan Mobley": "埃文·莫布利",
    "Paolo Banchero": "保罗·班切罗",
    "Franz Wagner": "弗朗茨·瓦格纳",
    "Cade Cunningham": "凯德·坎宁安",
    "Jalen Suggs": "杰伦·萨格斯",
    "Victor Wembanyama": "维克托·文班亚马",
    "DeMar DeRozan": "德玛尔·德罗赞",
    "Zach LaVine": "扎克·拉文",
    "Nikola Vucevic": "尼古拉·武切维奇",
    "LaMelo Ball": "拉梅洛·鲍尔",
    "Miles Bridges": "迈尔斯·布里奇斯",
    "Anthony Edwards": "安东尼·爱德华兹",
    "Rudy Gobert": "鲁迪·戈贝尔",
    "Karl-Anthony Towns": "卡尔-安东尼·唐斯",
    "Dejounte Murray": "德章泰·穆雷",
    "De'Andre Hunter": "德安德烈·亨特",
    "Onyeka Okongwu": "奥涅卡·奥孔古",
    "Clint Capela": "克林特·卡佩拉",
    "Bogdan Bogdanovic": "博格丹·博格达诺维奇",
    "John Collins": "约翰·科林斯",
    "Jalen Johnson": "杰伦·约翰逊",
    "Dyson Daniels": "戴森·丹尼尔斯",
    "Trey Hillman": "特雷·希曼",  # 示例，实际可能不存在
    # 可继续扩展...
}

def translate_player_name(name):
    """将英文球员名转为中文，若无则返回原名"""
    return player_translation.get(name.strip(), name)

# ====== 其余函数保持不变，仅在 parse_player_stats 中加入翻译 ======

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
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return data
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

def parse_player_stats(game_data):
    try:
        players_section = game_data.get('boxscore', {}).get('players', [])
        if not players_section or len(players_section) < 2:
            return [], []

        home_players = players_section[0]
        away_players = players_section[1]

        def extract_team_data(team_data):
            stats_list = team_data.get('statistics', [])
            if not stats_list:
                return []
            main_stat = stats_list[0]
            labels = main_stat.get('labels', [])
            athletes = main_stat.get('athletes', [])
            
            parsed = []
            for ath in athletes:
                name_en = ath.get('athlete', {}).get('displayName', '').strip()
                name_cn = translate_player_name(name_en)  # <<< 关键：翻译球员名
                raw_vals = ath.get('stats', [])
                if not name_en or not raw_vals:
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
                    '球员': name_cn,  # <<< 使用中文名
                    '时间': format_time(minutes),
                    '得分': pts,
                    '投篮': f"{fgm}/{fga}",
                    '三分': f"{threepm}/{threepa}",
                    '罚球': f"{ftm}/{fta}",
                    '篮板': reb,
                    '助攻': ast,
                    '失误': tov
                })
            return parsed

        home_data = extract_team_data(home_players)
        away_data = extract_team_data(away_players)

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

    home = competitors[0]
    away = competitors[1]

    home_name = translate_team_name(home.get('team', {}).get('displayName', '主队'))
    away_name = translate_team_name(away.get('team', {}).get('displayName', '客队'))
    home_score = home.get('score', '0')
    away_score = away.get('score', '0')

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
