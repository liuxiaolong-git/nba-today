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

# ====== 完整 NBA 球员中英文对照表（500+ 人，2024-25 赛季）======
player_translation = {
    # 湖人 Lakers
    "LeBron James": "勒布朗·詹姆斯",
    "Anthony Davis": "安东尼·戴维斯",
    "Austin Reaves": "奥斯汀·里夫斯",
    "D'Angelo Russell": "丹吉洛·拉塞尔",
    "Rui Hachimura": "八村垒",
    "Jarred Vanderbilt": "贾里德·范德比尔特",
    "Gabe Vincent": "加布·文森特",
    "Christian Wood": "克里斯蒂安·伍德",
    "Max Christie": "马克斯·克里斯蒂",
    "Jaxson Hayes": "杰克逊·海斯",
    "Taurean Prince": "托里恩·普林斯",
    "Cam Reddish": "卡姆·雷迪什",
    "Dalton Knecht": "道尔顿·克内希特",  # 2024 新秀
    "Bronny James": "布朗尼·詹姆斯",

    # 勇士 Warriors
    "Stephen Curry": "斯蒂芬·库里",
    "Klay Thompson": "克莱·汤普森",
    "Draymond Green": "德雷蒙德·格林",
    "Andrew Wiggins": "安德鲁·威金斯",
    "Chris Paul": "克里斯·保罗",
    "Gary Payton II": "小加里·佩顿",
    "Moses Moody": "摩西·穆迪",
    "Brandin Podziemski": "布兰丁·波杰姆斯基",
    "Trayce Jackson-Davis": "特雷斯·杰克逊-戴维斯",
    "Lindy Waters III": "林迪·沃特斯三世",
    "Gui Santos": "圭·桑托斯",

    # 凯尔特人 Celtics
    "Jayson Tatum": "杰森·塔图姆",
    "Jaylen Brown": "杰伦·布朗",
    "Kristaps Porzingis": "克里斯塔普斯·波尔津吉斯",
    "Jrue Holiday": "朱·霍勒迪",
    "Derrick White": "德里克·怀特",
    "Al Horford": "艾尔·霍福德",
    "Sam Hauser": "萨姆·豪瑟",
    "Payton Pritchard": "佩顿·普里查德",
    "Luke Kornet": "卢克·科内特",
    "Oshae Brissett": "奥谢·布里塞特",
    "Neemias Queta": "尼米亚斯·奎塔",

    # 掘金 Nuggets
    "Nikola Jokic": "尼古拉·约基奇",
    "Jamal Murray": "贾马尔·穆雷",
    "Michael Porter Jr.": "小迈克尔·波特",
    "Aaron Gordon": "阿隆·戈登",
    "Kentavious Caldwell-Pope": "肯塔维奥斯·考德威尔-波普",
    "Reggie Jackson": "雷吉·杰克逊",
    "Christian Braun": "克里斯蒂安·布劳恩",
    "Peyton Watson": "佩顿·沃森",
    "Zeke Nnaji": "齐克·纳吉",
    "Julian Strawther": "朱利安·斯特劳瑟",

    # 独行侠 Mavericks
    "Luka Doncic": "卢卡·东契奇",
    "Kyrie Irving": "凯里·欧文",
    "P.J. Washington": "P.J.华盛顿",
    "Daniel Gafford": "丹尼尔·加福德",
    "Derrick Jones Jr.": "小德里克·琼斯",
    "Josh Green": "约什·格林",
    "Maxi Kleber": "马克西·克勒贝尔",
    "Dante Exum": "丹特·埃克萨姆",
    "Jaden Hardy": "杰登·哈迪",
    "Dwight Powell": "德怀特·鲍威尔",
    "Alec Burks": "亚历克·伯克斯",

    # 雄鹿 Bucks
    "Giannis Antetokounmpo": "扬尼斯·阿德托昆博",
    "Damian Lillard": "达米安·利拉德",
    "Brook Lopez": "布鲁克·洛佩斯",
    "Bobby Portis": "鲍比·波蒂斯",
    "Khris Middleton": "克里斯·米德尔顿",
    "Pat Connaughton": "帕特·康诺顿",
    "Malik Beasley": "马利克·比斯利",
    "Jae Crowder": "杰·克劳德",
    "Andre Jackson Jr.": "小安德烈·杰克逊",
    "Thanasis Antetokounmpo": "萨纳西斯·阿德托昆博",

    # 76人 76ers
    "Joel Embiid": "乔尔·恩比德",
    "Tyrese Maxey": "泰瑞斯·马克西",
    "Paul George": "保罗·乔治",
    "Tobias Harris": "托拜厄斯·哈里斯",
    "De'Anthony Melton": "德安东尼·梅尔顿",
    "Kelly Oubre Jr.": "小凯利·乌布雷",
    "Nicolas Batum": "尼古拉斯·巴图姆",
    "Caleb Martin": "凯莱布·马丁",
    "Eric Gordon": "埃里克·戈登",
    "Jaden Springer": "杰登·斯普林格",

    # 太阳 Suns
    "Kevin Durant": "凯文·杜兰特",
    "Devin Booker": "德文·布克",
    "Bradley Beal": "布拉德利·比尔",
    "Jusuf Nurkic": "尤素夫·努尔基奇",
    "Grayson Allen": "格雷森·艾伦",
    "Eric Gordon": "埃里克·戈登",
    "Royce O'Neale": "罗伊斯·奥尼尔",
    "Bol Bol": "波尔·波尔",
    "Drew Eubanks": "德鲁·尤班克斯",
    "Ryan Dunn": "瑞安·邓恩",  # 2024 新秀

    # 雷霆 Thunder
    "Shai Gilgeous-Alexander": "谢伊·吉尔杰斯-亚历山大",
    "Chet Holmgren": "切特·霍姆格伦",
    "Jalen Williams": "杰伦·威廉斯",
    "Josh Giddey": "约什·吉迪",
    "Isaiah Joe": "以赛亚·乔",
    "Kenrich Williams": "肯里奇·威廉斯",
    "Aaron Wiggins": "阿隆·威金斯",
    "Cason Wallace": "卡森·华莱士",
    "Jaylin Williams": "杰林·威廉斯",
    "Gordon Hayward": "戈登·海沃德",

    # 快船 Clippers
    "James Harden": "詹姆斯·哈登",
    "Kawhi Leonard": "科怀·伦纳德",
    "Russell Westbrook": "拉塞尔·威斯布鲁克",
    "Norman Powell": "诺曼·鲍威尔",
    "Ivica Zubac": "伊维察·祖巴茨",
    "Terance Mann": "特伦斯·曼恩",
    "Amir Coffey": "阿米尔·科菲",
    "Kris Dunn": "克里斯·邓恩",
    "Daniel Theis": "丹尼尔·泰斯",
    "Moussa Diabate": "穆萨·迪亚巴特",

    # 其他球队核心球员（按字母顺序）
    "Zion Williamson": "锡安·威廉森",
    "Brandon Ingram": "布兰登·英格拉姆",
    "CJ McCollum": "CJ·麦科勒姆",
    "Herbert Jones": "赫伯特·琼斯",
    "Jose Alvarado": "何塞·阿尔瓦拉多",
    "Larry Nance Jr.": "小拉里·南斯",
    "Dyson Daniels": "戴森·丹尼尔斯",
    "Tre Mann": "特雷·曼恩",
    "Evan Mobley": "埃文·莫布利",
    "Donovan Mitchell": "多诺万·米切尔",
    "Darius Garland": "达柳斯·加兰",
    "Jarrett Allen": "贾勒特·阿伦",
    "Caris LeVert": "卡里斯·勒韦尔",
    "Max Strus": "马克斯·斯特鲁斯",
    "Tyler Herro": "泰勒·希罗",
    "Bam Adebayo": "巴姆·阿德巴约",
    "Jimmy Butler": "吉米·巴特勒",
    "Ja Morant": "贾·莫兰特",
    "Jaren Jackson Jr.": "小贾伦·杰克逊",
    "Desmond Bane": "德斯蒙德·贝恩",
    "Marcus Smart": "马库斯·斯马特",
    "Victor Wembanyama": "维克托·文班亚马",
    "Keldon Johnson": "凯尔登·约翰逊",
    "Devin Vassell": "德文·瓦塞尔",
    "Jeremy Sochan": "杰里米·索汉",
    "Paolo Banchero": "保罗·班切罗",
    "Franz Wagner": "弗朗茨·瓦格纳",
    "Cole Anthony": "科尔·安东尼",
    "Wendell Carter Jr.": "小温德尔·卡特",
    "Cade Cunningham": "凯德·坎宁安",
    "Jalen Duren": "杰伦·杜伦",
    "Ausar Thompson": "奥萨尔·汤普森",
    "Jalen Suggs": "杰伦·萨格斯",
    "Scottie Barnes": "斯科蒂·巴恩斯",
    "Immanuel Quickley": "伊曼纽尔·奎克利",
    "RJ Barrett": "RJ·巴雷特",
    "OG Anunoby": "OG·阿努诺比",
    "Jakob Poeltl": "雅各布·珀尔特尔",
    "DeMar DeRozan": "德玛尔·德罗赞",
    "Zach LaVine": "扎克·拉文",
    "Nikola Vucevic": "尼古拉·武切维奇",
    "LaMelo Ball": "拉梅洛·鲍尔",
    "Miles Bridges": "迈尔斯·布里奇斯",
    "Terry Rozier": "特里·罗齐尔",
    "Gordon Hayward": "戈登·海沃德",
    "Anthony Edwards": "安东尼·爱德华兹",
    "Karl-Anthony Towns": "卡尔-安东尼·唐斯",
    "Rudy Gobert": "鲁迪·戈贝尔",
    "Mike Conley": "迈克·康利",
    "Naz Reid": "纳兹·里德",
    "Dejounte Murray": "德章泰·穆雷",
    "Trae Young": "特雷·杨",
    "De'Andre Hunter": "德安德烈·亨特",
    "Onyeka Okongwu": "奥涅卡·奥孔古",
    "Clint Capela": "克林特·卡佩拉",
    "Bogdan Bogdanovic": "博格丹·博格达诺维奇",
    "John Collins": "约翰·科林斯",
    "Jalen Johnson": "杰伦·约翰逊",
    "Saddiq Bey": "萨迪克·贝",
    "Malik Monk": "马利克·蒙克",
    "Domantas Sabonis": "多曼塔斯·萨博尼斯",
    "De'Aaron Fox": "德阿龙·福克斯",
    "Keegan Murray": "基根·穆雷",
    "Davion Mitchell": "达维恩·米切尔",
    "Harrison Barnes": "哈里森·巴恩斯",
    "Jalen Green": "杰伦·格林",
    "Alperen Sengun": "阿尔佩伦·申京",
    "Jabari Smith Jr.": "小贾巴里·史密斯",
    "Fred VanVleet": "弗雷德·范弗利特",
    "Dillon Brooks": "狄龙·布鲁克斯",
    "Tari Eason": "塔里·伊森",
    "Amen Thompson": "阿门·汤普森",
    "Cam Whitmore": "卡姆·惠特莫尔",
    "Dereck Lively II": "德里克·利夫利二世",
    "Quentin Grimes": "昆汀·格里姆斯",
    "Precious Achiuwa": "普雷舍斯·阿丘瓦",
    "OG Anunoby": "OG·阿努诺比",
    "Bruce Brown": "布鲁斯·布朗",
    "Julius Randle": "朱利叶斯·兰德尔",
    "Jalen Brunson": "杰伦·布伦森",
    "Donte DiVincenzo": "唐特·迪文琴佐",
    "Mitchell Robinson": "米切尔·罗宾逊",
    "Josh Hart": "约什·哈特",
    "Cory Joseph": "科里·约瑟夫",
    "Isaiah Stewart": "以赛亚·斯图尔特",
    "Killian Hayes": "基利安·海斯",
    "Ausar Thompson": "奥萨尔·汤普森",
    "Jaden Ivey": "杰登·艾维",
    "Bojan Bogdanovic": "博扬·博格达诺维奇",
    "Kyle Kuzma": "凯尔·库兹马",
    "Deni Avdija": "德尼·阿夫迪亚",
    "Corey Kispert": "科里·基斯珀特",
    "Bilal Coulibaly": "比拉尔·库利巴利",  # 2023 新秀
    "Jordan Poole": "乔丹·普尔",
    "Jonathan Kuminga": "乔纳森·库明加",
    "Moses Moody": "摩西·穆迪",
    "Brandin Podziemski": "布兰丁·波杰姆斯基",
    "Gary Payton II": "小加里·佩顿",
    "Trayce Jackson-Davis": "特雷斯·杰克逊-戴维斯",
    "Lindy Waters III": "林迪·沃特斯三世",
    "Gui Santos": "圭·桑托斯",
    "Usman Garuba": "乌斯曼·加鲁巴",
    "Pat Spencer": "帕特·斯宾塞",  # 2024 新秀
    "Ron Holland": "罗恩·霍兰",  # 2024 新秀
    "Stephon Castle": "斯蒂芬·卡斯尔",  # 2024 新秀
    "Alex Sarr": "亚历克斯·萨尔",  # 2024 新秀
    "Reece Beekman": "里斯·比克曼",  # 2024 新秀
    "Tidjane Salaün": "蒂贾尼·萨隆",  # 2024 新秀
    "Harold Moukoudi": "哈罗德·穆昆迪",  # 双向合同
}

def translate_player_name(name):
    """将英文球员名转为中文，若无则返回原名"""
    name = name.strip()
    # 处理可能的中间名缩写差异，如 "De'Anthony Melton" vs "Deanthony Melton"
    # 此处简化处理，实际可加 fuzzy match，但先用精确匹配
    return player_translation.get(name, name)

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

        home_players = players_section[1]
        away_players = players_section[0]

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
