import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程")

if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0
    
if 'untranslated_players' not in st.session_state:
    st.session_state.untranslated_players = set()

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

# ====== 完整 NBA 球员中英文对照表 ======
player_translation = {
    "LeBron James": "勒布朗·詹姆斯",
    "Stephen Curry": "斯蒂芬·库里",
    "Kevin Durant": "凯文·杜兰特",
    "Giannis Antetokounmpo": "扬尼斯·阿德托昆博",
    "Joel Embiid": "乔尔·恩比德",
    "Nikola Jokic": "尼古拉·约基奇",
    "Luka Doncic": "卢卡·东契奇",
    "Duane Washington Jr": "小杜安·华盛顿",
    "John Butler Jr": "小约翰·巴特勒",
    "Scotty Pippen Jr": "小斯科蒂·皮蓬",
    "Vince Williams Jr": "小文斯·威廉姆斯",
    "Dereck Lively II": "德里克·利夫利二世",
    "Marcus Morris Sr": "马库斯·莫里斯",
    "Robert Williams III": "罗伯特·威廉斯三世",
    "Greg Brown III": "格雷格·布朗三世",
    "Trey Murphy III": "特雷·墨菲三世",
    "Lonnie Walker IV": "朗尼·沃克四世",
    "AJ Green": "AJ·格林",
    "RJ Barrett": "RJ·巴雷特",
    "CJ McCollum": "CJ·麦科勒姆",
    "PJ Washington": "PJ·华盛顿",
    "OG Anunoby": "OG·阿努诺比",
    "TJ McConnell": "T.J.麦康奈尔",
    "GG Jackson": "GG·杰克逊",
    "KJ Martin": "KJ·马丁",
    "JT Thor": "JT·索尔",
    "Anthony Davis": "安东尼·戴维斯",
    "Kawhi Leonard": "科怀·伦纳德",
    "Paul George": "保罗·乔治",
    "James Harden": "詹姆斯·哈登",
    "Russell Westbrook": "拉塞尔·威斯布鲁克",
    "Kyrie Irving": "凯里·欧文",
    "Damian Lillard": "达米安·利拉德",
    "Jayson Tatum": "杰森·塔图姆",
    "Jaylen Brown": "杰伦·布朗",
    "Devin Booker": "德文·布克",
    "Chris Paul": "克里斯·保罗",
    "Karl-Anthony Towns": "卡尔-安东尼·唐斯",
    "Anthony Edwards": "安东尼·爱德华兹",
    "Zion Williamson": "蔡恩·威廉森",
    "Ja Morant": "贾·莫兰特",
    "Trae Young": "特雷·杨",
    "DeMar DeRozan": "德马尔·德罗赞",
    "Zach LaVine": "扎克·拉文",
    "Donovan Mitchell": "多诺万·米切尔",
    "Darius Garland": "达柳斯·加兰",
    "Jarrett Allen": "贾勒特·阿伦",
    "Bam Adebayo": "巴姆·阿德巴约",
    "Jimmy Butler": "吉米·巴特勒",
    "Kyle Lowry": "凯尔·洛瑞",
    "De'Aaron Fox": "达龙·福克斯",
    "Domantas Sabonis": "多曼塔斯·萨博尼斯",
    "LaMelo Ball": "拉梅洛·鲍尔",
    "Tyrese Haliburton": "泰雷斯·哈利伯顿",
    "Pascal Siakam": "帕斯卡尔·西亚卡姆",
    "Fred VanVleet": "弗雷德·范弗利特",
    "Scottie Barnes": "斯科蒂·巴恩斯",
    "Jalen Brunson": "杰伦·布伦森",
    "Julius Randle": "朱利叶斯·兰德尔",
    "Shai Gilgeous-Alexander": "谢伊·吉尔杰斯-亚历山大",
    "Jalen Williams": "杰伦·威廉姆斯",
    "Chet Holmgren": "切特·霍姆格伦",
    "Josh Giddey": "约什·吉迪",
    "Franz Wagner": "弗朗茨·瓦格纳",
    "Paolo Banchero": "保罗·班凯罗",
    "Jalen Suggs": "杰伦·萨格斯",
    "Tyrese Maxey": "泰雷斯·马克西",
    "Joel Embiid": "乔尔·恩比德",
    "James Harden": "詹姆斯·哈登",
    "Tyrese Maxey": "泰雷斯·马克西",
    "Devin Booker": "德文·布克",
    "Bradley Beal": "布拉德利·比尔",
    "Jusuf Nurkic": "优素福·努尔基奇",
    "Anfernee Simons": "安芬尼·西蒙斯",
    "Jerami Grant": "杰拉米·格兰特",
    "Deandre Ayton": "德安德烈·艾顿",
    "Keegan Murray": "基根·默里",
    "De'Aaron Fox": "达龙·福克斯",
    "Victor Wembanyama": "维克托·文班亚马",
    "Devin Vassell": "德文·瓦塞尔",
    "Keldon Johnson": "凯尔登·约翰逊",
    "Jordan Clarkson": "乔丹·克拉克森",
    "Lauri Markkanen": "劳里·马尔卡宁",
    "Walker Kessler": "沃克·凯斯勒",
    "Kyle Kuzma": "凯尔·库兹马",
    "Jordan Poole": "乔丹·普尔",
    "Tyus Jones": "泰厄斯·琼斯",
}

def translate_player_name(name):
    """将英文球员名转为中文，若无则返回原名"""
    if not name:
        return name
    
    name = name.strip()
    
    # 首先尝试完全匹配
    if name in player_translation:
        return player_translation[name]
    
    # 尝试处理Jr./Sr./II/III/IV等后缀
    name_parts = name.split()
    if len(name_parts) > 1:
        # 定义常见的后缀
        suffixes = ['Jr.', 'Jr', 'Sr.', 'Sr', 'II', 'III', 'IV', 'V']
        
        # 检查最后一个部分是否是后缀
        if name_parts[-1] in suffixes:
            base_name = ' '.join(name_parts[:-1])
            
            # 尝试匹配基础名称
            if base_name in player_translation:
                translated_base = player_translation[base_name]
                suffix = name_parts[-1]
                suffix_map = {
                    'Jr.': '小', 'Jr': '小',
                    'Sr.': '老', 'Sr': '老',
                    'II': '二世', 'III': '三世', 'IV': '四世', 'V': '五世'
                }
                if suffix in suffix_map:
                    return f"{translated_base}{suffix_map[suffix]}"
                return translated_base
    
    # 模糊匹配：忽略中间名缩写
    if '.' in name:
        # 将 "A.J. Green" 转换为 "AJ Green" 等
        simple_name = name.replace('.', '').replace(' ', '')
        for eng_name in player_translation:
            simple_eng = eng_name.replace('.', '').replace(' ', '')
            if simple_name.lower() == simple_eng.lower():
                return player_translation[eng_name]
    
    # 部分匹配：检查是否有相似的名字
    for eng_name, chi_name in player_translation.items():
        # 忽略大小写比较
        if eng_name.lower() in name.lower() or name.lower() in eng_name.lower():
            return chi_name
    
    # 尝试匹配不带"小"前缀的中文名
    if '小' not in name:
        for eng_name, chi_name in player_translation.items():
            if chi_name.startswith('小') and eng_name in name:
                return chi_name
    
    # 记录未翻译的名称以便调试
    if name not in ['DNP', 'N/A', '--', '']:
        st.session_state.untranslated_players.add(name)
    
    return name  # 返回原名

# ====== API 数据获取函数 ======
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
        # 尝试第一个API端点
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return data
        
        # 如果第一个失败，尝试第二个API端点
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/boxscore?event={event_id}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
            
        return None
    except Exception as e:
        return None

def format_time(t):
    """格式化时间"""
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

def safe_int(value, default=0):
    """安全地将值转换为整数"""
    if not value:
        return default
    try:
        # 处理 "5/10" 这样的投篮数据
        if '/' in str(value):
            return int(str(value).split('/')[0])
        # 处理纯数字
        return int(float(str(value)))
    except:
        return default

def parse_player_stats(game_data):
    """解析球员统计数据"""
    try:
        if not game_data or 'boxscore' not in game_data:
            return [], []
            
        players_section = game_data.get('boxscore', {}).get('players', [])
        if not players_section or len(players_section) < 2:
            return [], []

        # 尝试按索引获取主客场球员数据
        home_players = None
        away_players = None
        
        # 首先尝试通过索引获取
        if len(players_section) >= 2:
            away_players = players_section[0]
            home_players = players_section[1]
        else:
            # 如果只有一组数据，可能是不同的结构
            return [], []

        def extract_team_data(team_data):
            """提取单个球队的球员数据"""
            if not team_data:
                return []
                
            stats_list = team_data.get('statistics', [])
            if not stats_list:
                return []
                
            # 查找主要统计项（通常第一个是球员统计）
            main_stat = None
            for stat in stats_list:
                athletes = stat.get('athletes', [])
                labels = stat.get('labels', [])
                if athletes and ('PTS' in labels or '得分' in labels):
                    main_stat = stat
                    break
            
            if not main_stat:
                return []
                
            labels = main_stat.get('labels', [])
            athletes = main_stat.get('athletes', [])
            
            parsed = []
            for ath in athletes:
                try:
                    # 获取球员名
                    athlete_data = ath.get('athlete', {})
                    name_en = (athlete_data.get('displayName', '') or 
                              athlete_data.get('fullName', '') or 
                              athlete_data.get('shortName', '') or 
                              ath.get('displayName', '') or 
                              ath.get('name', ''))
                    
                    name_en = str(name_en).strip()
                    if not name_en or name_en in ['DNP', 'N/A', '--', 'null', 'None', 'DID NOT PLAY', 'NOT AVAILABLE']:
                        continue
                    
                    # 翻译球员名
                    name_cn = translate_player_name(name_en)
                    
                    raw_vals = ath.get('stats', [])
                    if not raw_vals:
                        continue
                    
                    # 创建统计映射
                    stat_map = {}
                    for i, label in enumerate(labels):
                        if i < len(raw_vals):
                            value = raw_vals[i]
                            if isinstance(value, (int, float)):
                                value = str(value)
                            elif value is None:
                                value = ''
                            else:
                                value = str(value).strip()
                            stat_map[label] = value
                    
                    # 安全地获取各项数据
                    def get_shot_value(key, default='0-0'):
                        value = stat_map.get(key, default)
                        if not value:
                            value = default
                        return str(value)
                    
                    def get_stat_value(key, default='0'):
                        value = stat_map.get(key, default)
                        if not value:
                            value = default
                        return str(value)
                    
                    # 解析投篮数据
                    fg_str = get_shot_value('FG', '0-0').replace('/', '-')
                    three_str = get_shot_value('3PT', '0-0').replace('/', '-')
                    ft_str = get_shot_value('FT', '0-0').replace('/', '-')
                    
                    # 分割投篮数据
                    fg_parts = fg_str.split('-') if '-' in fg_str else ('0', '0')
                    three_parts = three_str.split('-') if '-' in three_str else ('0', '0')
                    ft_parts = ft_str.split('-') if '-' in ft_str else ('0', '0')
                    
                    fgm = fg_parts[0] if len(fg_parts) >= 1 else '0'
                    fga = fg_parts[1] if len(fg_parts) >= 2 else '0'
                    threepm = three_parts[0] if len(three_parts) >= 1 else '0'
                    threepa = three_parts[1] if len(three_parts) >= 2 else '0'
                    ftm = ft_parts[0] if len(ft_parts) >= 1 else '0'
                    fta = ft_parts[1] if len(ft_parts) >= 2 else '0'
                    
                    # 确保数字有效性
                    def safe_num(val):
                        try:
                            num = float(val)
                            return str(int(num)) if num.is_integer() else str(round(num, 1))
                        except:
                            return '0'
                    
                    # 获取其他统计
                    minutes = format_time(stat_map.get('MIN', '0'))
                    pts = safe_num(get_stat_value('PTS', '0'))
                    reb = safe_num(get_stat_value('REB', '0'))
                    ast = safe_num(get_stat_value('AST', '0'))
                    tov = safe_num(get_stat_value('TO', '0'))
                    
                    # 创建球员数据字典
                    player_data = {
                        '球员': name_cn,
                        '时间': minutes,
                        '得分': pts,
                        '投篮': f"{fgm}/{fga}",
                        '三分': f"{threepm}/{threepa}",
                        '罚球': f"{ftm}/{fta}",
                        '篮板': reb,
                        '助攻': ast,
                        '失误': tov
                    }
                    
                    # 只添加有数据的球员（至少得分、篮板、助攻或时间不为0）
                    has_data = False
                    if (safe_int(pts) > 0 or safe_int(reb) > 0 or safe_int(ast) > 0 or 
                        safe_int(fgm) > 0 or safe_int(threepm) > 0 or safe_int(ftm) > 0):
                        has_data = True
                    
                    # 检查上场时间是否大于0
                    if minutes != '0:00' and minutes != '0':
                        has_data = True
                    
                    if has_data:
                        parsed.append(player_data)
                        
                except Exception as e:
                    # 跳过单个球员的错误
                    continue
            
            return parsed

        away_data = extract_team_data(away_players)
        home_data = extract_team_data(home_players)

        return away_data, home_data

    except Exception as e:
        return [], []

# ====== Streamlit 界面 ======
# Sidebar
with st.sidebar:
    st.header("⚙️ 查询设置")
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3)
    )
    
    if st.button("🧹 清除缓存"):
        st.cache_data.clear()
        st.success("缓存已清除")

# Main
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

with st.spinner("加载赛程..."):
    schedule = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule or 'events' not in schedule:
    st.error("无法获取数据，请稍后重试")
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

    # 显示比赛信息
    cols = st.columns([2, 1, 0.5, 1, 2])
    cols[0].markdown(f"**{away_name}**")
    cols[1].markdown(f"**{away_score}**")
    cols[2].markdown("**VS**")
    cols[3].markdown(f"**{home_score}**")
    cols[4].markdown(f"**{home_name}**")
    st.caption(f"{badge} | {desc} | ⏰ {bj_time}")

    # 如果比赛进行中或已结束，显示球员数据
    if state in ['in', 'post']:
        with st.spinner(f"加载{away_name} vs {home_name}的球员数据..."):
            game_data = fetch_player_stats(event['id'])
            if game_data:
                away_p, home_p = parse_player_stats(game_data)
                
                # 只显示有数据的比赛
                if away_p or home_p:
                    st.subheader("📊 球员数据")
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown(f"**{away_name}**")
                        if away_p:
                            df = pd.DataFrame(away_p)
                            if not df.empty:
                                # 按得分排序
                                df['得分'] = pd.to_numeric(df['得分'], errors='coerce')
                                df = df.sort_values('得分', ascending=False)
                                df['得分'] = df['得分'].astype(str)
                                st.dataframe(df, hide_index=True, use_container_width=True)
                            else:
                                st.info("暂无球员数据")
                        else:
                            st.info("暂无球员数据")
                    
                    with c2:
                        st.markdown(f"**{home_name}**")
                        if home_p:
                            df = pd.DataFrame(home_p)
                            if not df.empty:
                                # 按得分排序
                                df['得分'] = pd.to_numeric(df['得分'], errors='coerce')
                                df = df.sort_values('得分', ascending=False)
                                df['得分'] = df['得分'].astype(str)
                                st.dataframe(df, hide_index=True, use_container_width=True)
                            else:
                                st.info("暂无球员数据")
                        else:
                            st.info("暂无球员数据")
                else:
                    # 只有比赛状态为进行中或已结束但没有数据时才显示提示
                    st.info("球员数据暂未更新，请稍后刷新")
            else:
                st.warning("球员数据加载失败，请稍后重试")

    if i < len(events) - 1:
        st.divider()

st.divider()
col1, col2, col3 = st.columns([3, 1, 1])
col1.caption(f"更新于: {datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')}")

if col2.button("🔄 刷新数据"):
    st.cache_data.clear()
    st.rerun()

# 显示未翻译的球员名
if st.session_state.untranslated_players:
    with st.expander("⚠️ 未翻译球员名（需要添加到映射表）"):
        st.write("以下球员名未找到翻译，请添加到 `player_translation` 字典中：")
        for player in sorted(st.session_state.untranslated_players):
            st.text(f'"{player}": "",')
