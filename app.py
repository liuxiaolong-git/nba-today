import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程")

# 初始化 session state
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0
    
if 'untranslated_players' not in st.session_state:
    st.session_state.untranslated_players = set()

beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# ====== 从配置文件加载翻译数据（缓存30天） ======
@st.cache_data(ttl=2592000)  # 30天缓存
def load_translations():
    """加载球队和球员翻译数据"""
    try:
        # 从配置模块导入翻译数据
        from translations import TEAM_TRANSLATION, PLAYER_TRANSLATION
        return TEAM_TRANSLATION, PLAYER_TRANSLATION
    except ImportError:
        # 如果导入失败，使用默认的空字典
        st.warning("⚠️ 未找到翻译配置文件，使用默认翻译")
        return {}, {}

# 加载翻译数据
team_translation, player_translation = load_translations()

def translate_team_name(name):
    """翻译球队名称"""
    return team_translation.get(name, name)

def translate_player_name(name):
    """将英文球员名转为中文，若无则返回原名"""
    if not name:
        return name
    
    name = name.strip()
    
    # 首先尝试完全匹配
    if name in player_translation:
        return player_translation[name]
    
    # 尝试处理后缀
    name_parts = name.split()
    if len(name_parts) > 1:
        suffixes = ['Jr.', 'Jr', 'Sr.', 'Sr', 'II', 'III', 'IV', 'V']
        if name_parts[-1] in suffixes:
            base_name = ' '.join(name_parts[:-1])
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
    
    # 尝试标准化匹配（移除点号）
    normalized = name.replace('.', '')
    if normalized in player_translation:
        return player_translation[normalized]
    
    # 模糊匹配：忽略大小写
    for eng_name, chi_name in player_translation.items():
        if eng_name.lower() == name.lower():
            return chi_name
    
    # 记录未翻译的名称（排除无效值）
    invalid_names = ['DNP', 'N/A', '--', '', 'null', 'None', 'DID NOT PLAY', 'NOT AVAILABLE']
    if name not in invalid_names:
        st.session_state.untranslated_players.add(name)
    
    return name

# ====== API 数据获取函数 ======
@st.cache_data(ttl=30)  # 30秒缓存，实时数据
def fetch_nba_schedule(date_str):
    """获取NBA赛程"""
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

@st.cache_data(ttl=30)  # 30秒缓存，实时数据
def fetch_player_stats(event_id):
    """获取球员统计数据"""
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
        if '/' in str(value):
            return int(str(value).split('/')[0])
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

        # 获取主客场球员数据
        away_players = players_section[0]
        home_players = players_section[1]

        def extract_team_data(team_data):
            """提取单个球队的球员数据"""
            if not team_data:
                return []
                
            stats_list = team_data.get('statistics', [])
            if not stats_list:
                return []
                
            # 查找主要统计项
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
                    
                    # 解析投篮数据
                    def get_shot_value(key, default='0-0'):
                        value = stat_map.get(key, default)
                        return str(value) if value else default
                    
                    def get_stat_value(key, default='0'):
                        value = stat_map.get(key, default)
                        return str(value) if value else default
                    
                    # 获取投篮数据
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
                    
                    # 安全转换数字
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
                    
                    # 只添加有数据的球员
                    has_data = False
                    if (safe_int(pts) > 0 or safe_int(reb) > 0 or safe_int(ast) > 0 or 
                        safe_int(fgm) > 0 or safe_int(threepm) > 0 or safe_int(ftm) > 0):
                        has_data = True
                    
                    if minutes != '0:00' and minutes != '0':
                        has_data = True
                    
                    if has_data:
                        parsed.append(player_data)
                        
                except Exception:
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
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 刷新所有数据"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
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

# 显示比赛列表
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
        with st.spinner(f"加载球员数据..."):
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
                    st.info("球员数据暂未更新")

    if i < len(events) - 1:
        st.divider()

# 页脚信息
st.divider()
col1, col2 = st.columns([3, 1])
col1.caption(f"更新时间: {datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')}")

# 显示未翻译的球员名（调试用）
if st.session_state.untranslated_players:
    with st.expander("⚠️ 未翻译球员名"):
        truly_untranslated = []
        for player in sorted(st.session_state.untranslated_players):
            # 检查是否能在当前映射表中找到
            translated = translate_player_name(player)
            if translated == player:  # 如果返回原值，说明没有翻译
                truly_untranslated.append(player)
        
        if truly_untranslated:
            st.write(f"以下 {len(truly_untranslated)} 个球员名未找到翻译：")
            for player in truly_untranslated:
                st.code(f'"{player}": "",')
        else:
            st.success("✓ 所有球员名都已翻译！")
