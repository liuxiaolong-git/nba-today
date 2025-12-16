import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import time
import concurrent.futures # 用于并行请求球员数据

# 移动端优化配置
st.set_page_config(
    page_title="NBA赛程查询(菲同学)", 
    page_icon="🏀", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 移动端优化的CSS
st.markdown("""
<style>
    /* 移动端适配 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem !important;
        }
        .game-card {
            background: white;
            border-radius: 10px;
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .simple-table-container, .full-table-container {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin: 8px 0;
        }
        .full-table-container {
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        .dataframe {
            font-size: 12px !important;
        }
        .dataframe th, .dataframe td {
            padding: 6px 4px !important;
            white-space: nowrap;
        }
        .stButton > button {
            min-height: 40px;
            font-size: 14px;
            width: 100%;
        }
        .refresh-panel {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
            margin-top: 10px;
            border: 1px solid #dee2e6;
        }
        h1 { font-size: 20px !important; margin-bottom: 12px !important; }
        h2, h3 { font-size: 16px !important; }
        .team-name {
            font-size: 14px;
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 120px;
        }
        .game-time { font-size: 12px; color: #666; }
        .countdown {
            font-weight: bold;
            color: #2196F3;
            font-size: 13px;
        }
        .auto-refresh-on { color: #4CAF50; font-weight: bold; }
        .auto-refresh-off { color: #9E9E9E; }
    }
    .live-game { border-left: 4px solid #4CAF50 !important; }
    .finished-game { border-left: 4px solid #9E9E9E !important; }
    .upcoming-game { border-left: 4px solid #2196F3 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🏀 NBA实时赛程(小包子)")

# ====== 【核心修复与优化点1：重新设计自动刷新逻辑】 ======
# 初始化自动刷新相关的session state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True  # 默认开启自动刷新
    
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30  # 默认30秒刷新一次
    
if 'last_refresh_time' not in st.session_state:
    # 使用时间戳而非datetime对象，避免序列化问题
    st.session_state.last_refresh_time = time.time()

# 初始化其他session state
if 'untranslated_players' not in st.session_state:
    st.session_state.untranslated_players = set()
if 'expanded_games' not in st.session_state:
    st.session_state.expanded_games = {}

beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# ====== 【核心优化点2：优化翻译数据加载】 ======
@st.cache_resource(ttl=600) # 缓存资源，10分钟刷新一次
def get_translations():
    """加载并返回翻译字典，使用cache_resource避免重复IO"""
    try:
        # 假设translations.py在同一目录
        from translations import TEAM_TRANSLATION, PLAYER_TRANSLATION
        return TEAM_TRANSLATION, PLAYER_TRANSLATION
    except ImportError:
        # 静默失败，返回空字典，避免警告信息影响加载
        return {}, {}

# 预加载翻译数据到变量，后续函数直接使用
_team_translation, _player_translation = get_translations()

def translate_team_name(name):
    return _team_translation.get(name, name)

def translate_player_name(name):
    if not name:
        return name
    name = name.strip()
    # 直接查找
    if name in _player_translation:
        return _player_translation[name]
    # 处理后缀逻辑 (保持原有)
    name_parts = name.split()
    if len(name_parts) > 1:
        suffixes = ['Jr.', 'Jr', 'Sr.', 'Sr', 'II', 'III', 'IV', 'V']
        if name_parts[-1] in suffixes:
            base_name = ' '.join(name_parts[:-1])
            if base_name in _player_translation:
                translated = _player_translation[base_name]
                suffix_map = {'Jr.':'小','Jr':'小','Sr.':'老','Sr':'老','II':'二世','III':'三世','IV':'四世','V':'五世'}
                return f"{translated}{suffix_map.get(name_parts[-1], '')}"
    # 记录未翻译的名称（简化判断）
    if name and name not in ['DNP', 'N/A', '--', '', 'null', 'None']:
        st.session_state.untranslated_players.add(name)
    return name

# ====== 【核心优化点3：优化API请求缓存与性能】 ======
@st.cache_data(ttl=15, show_spinner=False) # 缩短TTL为15秒，不显示加载spinner
def fetch_nba_schedule(date_str):
    """获取NBA赛程 - 主API，缓存15秒"""
    try:
        eastern = pytz.timezone('America/New_York')
        beijing_dt = beijing_tz.localize(datetime.strptime(date_str, '%Y-%m-%d'))
        eastern_dt = beijing_dt.astimezone(eastern)
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        params = {'dates': eastern_dt.strftime('%Y%m%d'), 'lang': 'zh', 'region': 'cn'}
        # 设置更短的超时时间，快速失败
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        # 静默失败，返回None由主逻辑处理
        return None

def fetch_single_player_stats(event_id):
    """获取单场比赛球员数据 - 无缓存，用于并行请求"""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return event_id, data
    except Exception:
        pass
    return event_id, None

def fetch_all_player_stats_parallel(event_ids):
    """并行获取多场比赛的球员数据"""
    player_stats_map = {}
    # 限制最大线程数，避免过多并发请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(event_ids))) as executor:
        future_to_id = {executor.submit(fetch_single_player_stats, eid): eid for eid in event_ids}
        for future in concurrent.futures.as_completed(future_to_id):
            event_id, data = future.result()
            if data:
                player_stats_map[event_id] = data
    return player_stats_map

# 辅助函数保持不变
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

def safe_int(value, default=0):
    if not value:
        return default
    try:
        if '/' in str(value):
            return int(str(value).split('/')[0])
        return int(float(str(value)))
    except:
        return default

def parse_player_stats(game_data):
    """解析球员统计数据 - 保持原始列结构"""
    try:
        if not game_data or 'boxscore' not in game_data:
            return [], []
        players_section = game_data.get('boxscore', {}).get('players', [])
        if not players_section or len(players_section) < 2:
            return [], []
        away_players, home_players = players_section[0], players_section[1]

        def extract_team_data(team_data):
            if not team_data:
                return []
            stats_list = team_data.get('statistics', [])
            main_stat = None
            for stat in stats_list:
                if stat.get('athletes') and ('PTS' in stat.get('labels', []) or '得分' in stat.get('labels', [])):
                    main_stat = stat
                    break
            if not main_stat:
                return []
            labels = main_stat.get('labels', [])
            athletes = main_stat.get('athletes', [])
            parsed = []
            for ath in athletes:
                try:
                    athlete_data = ath.get('athlete', {})
                    name_en = (athlete_data.get('displayName') or athlete_data.get('fullName') or 
                               athlete_data.get('shortName') or ath.get('displayName') or ath.get('name') or '')
                    name_en = str(name_en).strip()
                    if not name_en or name_en in ['DNP', 'N/A', '--', 'null', 'None']:
                        continue
                    name_cn = translate_player_name(name_en)
                    raw_vals = ath.get('stats', [])
                    if not raw_vals:
                        continue
                    stat_map = {}
                    for i, label in enumerate(labels):
                        if i < len(raw_vals):
                            val = raw_vals[i]
                            stat_map[label] = str(val).strip() if val is not None else ''
                    # 简化统计值获取
                    def get_stat(k, d='0'): return stat_map.get(k, d)
                    def get_shot(k, d='0-0'): return get_stat(k, d).replace('/', '-')
                    fg_part = get_shot('FG', '0-0').split('-')
                    three_part = get_shot('3PT', '0-0').split('-')
                    ft_part = get_shot('FT', '0-0').split('-')
                    player_data = {
                        '球员': name_cn,
                        '时间': format_time(get_stat('MIN', '0')),
                        '得分': get_stat('PTS', '0'),
                        '投篮': f"{fg_part[0] if len(fg_part)>1 else '0'}/{fg_part[1] if len(fg_part)>1 else '0'}",
                        '三分': f"{three_part[0] if len(three_part)>1 else '0'}/{three_part[1] if len(three_part)>1 else '0'}",
                        '罚球': f"{ft_part[0] if len(ft_part)>1 else '0'}/{ft_part[1] if len(ft_part)>1 else '0'}",
                        '篮板': get_stat('REB', '0'),
                        '助攻': get_stat('AST', '0'),
                        '失误': get_stat('TO', '0')
                    }
                    # 简化数据有效性检查
                    if (safe_int(player_data['得分']) > 0 or safe_int(player_data['篮板']) > 0 or 
                        safe_int(player_data['助攻']) > 0 or player_data['时间'] not in ('0:00', '0')):
                        parsed.append(player_data)
                except Exception:
                    continue
            return parsed
        away_data = extract_team_data(away_players)
        home_data = extract_team_data(home_players)
        return away_data, home_data
    except Exception:
        return [], []

def display_simple_table(players_data, team_name):
    """显示简化的表格（只显示球员、时间、得分）"""
    if not players_data:
        st.info("暂无球员数据")
        return
    players_data = sorted(players_data, key=lambda x: safe_int(x['得分'], 0), reverse=True)[:10]
    simple_data = [{'球员': p['球员'], '时间': p['时间'], '得分': p['得分']} for p in players_data]
    df = pd.DataFrame(simple_data)
    if not df.empty:
        st.markdown('<div class="simple-table-container">', unsafe_allow_html=True)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def display_full_table(players_data):
    """显示完整的球员数据表格"""
    if not players_data:
        st.info("暂无球员数据")
        return
    df = pd.DataFrame(players_data)
    if not df.empty:
        df['得分'] = pd.to_numeric(df['得分'], errors='coerce')
        df = df.sort_values('得分', ascending=False)
        df['得分'] = df['得分'].astype(str)
        st.markdown('<div class="full-table-container">', unsafe_allow_html=True)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ====== 【核心修复与优化点4：优化主界面与数据加载流程】 ======
# 顶部工具栏 - 移动端友好
col1, col2 = st.columns([3, 1])
with col1:
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3),
        label_visibility="collapsed"
    )

with col2:
    manual_refresh_clicked = st.button("🔄 刷新", use_container_width=True, key='manual_refresh_top')

# 【自动刷新触发逻辑】放在页面主要渲染之前，确保能被执行
current_time = time.time()
time_since_last_refresh = current_time - st.session_state.last_refresh_time
countdown_seconds = max(0, st.session_state.refresh_interval - int(time_since_last_refresh))

# 决定是否需要刷新：手动点击 OR (自动开启 AND 倒计时结束)
need_refresh = False
if manual_refresh_clicked:
    need_refresh = True
    st.session_state.last_refresh_time = current_time
    st.cache_data.clear()
elif st.session_state.auto_refresh and countdown_seconds <= 0:
    need_refresh = True
    st.session_state.last_refresh_time = current_time
    st.cache_data.clear()

# 如果需要刷新，则重新运行
if need_refresh:
    st.experimental_rerun()

# 显示日期标题
st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')}")

# 加载主赛程数据（带缓存）
with st.spinner("快速加载赛程..."):
    schedule = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule or 'events' not in schedule:
    st.error("无法获取数据，请稍后重试")
    st.stop()

events = schedule['events']
if not events:
    st.info("今日无比赛")
    st.stop()

# ====== 【核心优化点5：并行加载球员数据】 ======
# 识别需要球员数据的比赛（进行中或已结束）
live_or_post_event_ids = []
for event in events:
    status_type = event.get('status', {}).get('type', {})
    if status_type.get('state', 'pre') in ['in', 'post']:
        live_or_post_event_ids.append(event['id'])

player_stats_map = {}
if live_or_post_event_ids:
    # 并行请求球员数据
    with st.spinner("同步球员数据..."):
        player_stats_map = fetch_all_player_stats_parallel(live_or_post_event_ids)

# 渲染比赛列表
for i, event in enumerate(events):
    comp = event.get('competitions', [{}])[0]
    competitors = comp.get('competitors', [])
    if len(competitors) < 2:
        continue

    home, away = competitors[0], competitors[1]
    home_name = translate_team_name(home.get('team', {}).get('displayName', '主队'))
    away_name = translate_team_name(away.get('team', {}).get('displayName', '客队'))
    home_score = home.get('score', '0')
    away_score = away.get('score', '0')

    status_type = event.get('status', {}).get('type', {})
    state = status_type.get('state', 'pre')
    desc = status_type.get('description', '未开始')
    
    if state == 'in':
        status_badge, game_class = "🟢 直播中", "live-game"
    elif state == 'post':
        status_badge, game_class = "⚫ 已结束", "finished-game"
    else:
        status_badge, game_class = "⏳ 未开始", "upcoming-game"

    try:
        utc_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
        bj_time = utc_time.astimezone(beijing_tz).strftime("%H:%M")
    except:
        bj_time = "时间待定"

    # 比赛卡片
    st.markdown(f'<div class="game-card {game_class}">', unsafe_allow_html=True)
    cols = st.columns([2, 1, 2])
    with cols[0]:
        st.markdown(f'<div class="team-name">{away_name}</div>', unsafe_allow_html=True)
        st.markdown(f'**{away_score}**')
    with cols[1]:
        st.markdown("**VS**")
        st.markdown(f'<div class="game-time">{bj_time}</div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="team-name">{home_name}</div>', unsafe_allow_html=True)
        st.markdown(f'**{home_score}**')
    st.markdown(f'<span class="status-badge">{status_badge}</span> {desc}', unsafe_allow_html=True)
    
    # 球员数据
    if state in ['in', 'post']:
        game_data = player_stats_map.get(event['id'])
        if game_data:
            away_p, home_p = parse_player_stats(game_data)
            if away_p or home_p:
                game_key = f"game_{event['id']}"
                if game_key not in st.session_state.expanded_games:
                    st.session_state.expanded_games[game_key] = {'away_expanded': False, 'home_expanded': False}
                st.markdown("---")
                st.markdown("**球员数据**")
                tab1, tab2 = st.tabs([f"👤 {away_name}", f"👤 {home_name}"])
                with tab1:
                    if away_p:
                        st.markdown(f"**{away_name}**")
                        display_simple_table(away_p, away_name)
                        col_btn1, _ = st.columns([1, 1]) # 【修改：移除得分榜列】
                        with col_btn1:
                            if st.button("📊 详细数据", key=f"expand_away_{event['id']}", 
                                      use_container_width=True, 
                                      type="secondary" if not st.session_state.expanded_games[game_key]['away_expanded'] else "primary"):
                                st.session_state.expanded_games[game_key]['away_expanded'] = not st.session_state.expanded_games[game_key]['away_expanded']
                        if st.session_state.expanded_games[game_key]['away_expanded']:
                            st.markdown("**详细数据**")
                            display_full_table(away_p)
                    else:
                        st.info("暂无球员数据")
                with tab2:
                    if home_p:
                        st.markdown(f"**{home_name}**")
                        display_simple_table(home_p, home_name)
                        col_btn1, _ = st.columns([1, 1]) # 【修改：移除得分榜列】
                        with col_btn1:
                            if st.button("📊 详细数据", key=f"expand_home_{event['id']}", 
                                      use_container_width=True, 
                                      type="secondary" if not st.session_state.expanded_games[game_key]['home_expanded'] else "primary"):
                                st.session_state.expanded_games[game_key]['home_expanded'] = not st.session_state.expanded_games[game_key]['home_expanded']
                        if st.session_state.expanded_games[game_key]['home_expanded']:
                            st.markdown("**详细数据**")
                            display_full_table(home_p)
                    else:
                        st.info("暂无球员数据")
    st.markdown('</div>', unsafe_allow_html=True)
    if i < len(events) - 1:
        st.divider()

# ====== 【核心修复与优化点6：修复的自动刷新控制面板】 ======
st.markdown("---")
st.markdown('<div class="refresh-panel">', unsafe_allow_html=True)
st.markdown("### 🔄 自动刷新控制")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    # 此处的任何变更都会触发脚本重新运行
    auto_refresh = st.toggle(
        "自动刷新", 
        value=st.session_state.auto_refresh,
        help="开启后页面会自动定期刷新",
        key='auto_refresh_toggle' # 为toggle设置唯一key
    )
with col2:
    interval_options = [10, 30, 60, 120]
    refresh_interval = st.selectbox(
        "刷新间隔(秒)",
        options=interval_options,
        index=interval_options.index(st.session_state.refresh_interval) if st.session_state.refresh_interval in interval_options else 1,
        help="设置自动刷新的时间间隔",
        key='refresh_interval_select' # 为selectbox设置唯一key
    )
with col3:
    # 更新session state值
    if st.session_state.auto_refresh != auto_refresh:
        st.session_state.auto_refresh = auto_refresh
    if st.session_state.refresh_interval != refresh_interval:
        st.session_state.refresh_interval = refresh_interval
        st.session_state.last_refresh_time = current_time # 重置刷新时间
    
    # 显示状态
    if st.session_state.auto_refresh:
        status_text = f"状态: <span class='auto-refresh-on'>开启</span>"
        countdown_text = f"倒计时: <span class='countdown'>{countdown_seconds}秒</span>"
    else:
        status_text = "状态: <span class='auto-refresh-off'>关闭</span>"
        countdown_text = "倒计时: --"
    st.markdown(status_text, unsafe_allow_html=True)
    st.markdown(countdown_text, unsafe_allow_html=True)

# 手动刷新按钮（底部）
if st.button("🔄 立即手动刷新", use_container_width=True, type="primary", key='manual_refresh_bottom'):
    st.session_state.last_refresh_time = time.time()
    st.cache_data.clear()
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ====== 【核心修复点7：实现自动刷新的关键 - 前端元刷新】 ======
# 仅当自动刷新开启时，向前端注入HTML meta refresh标签
if st.session_state.auto_refresh:
    # 注：这里设置的刷新时间比间隔多1秒，给页面渲染留出时间
    refresh_seconds = st.session_state.refresh_interval + 1
    st.markdown(f"""
    <meta http-equiv="refresh" content="{refresh_seconds}">
    """, unsafe_allow_html=True)
    # 可选：在开发模式下显示一个小提示
    # st.caption(f"⏱️ 页面将在 {refresh_seconds} 秒后自动刷新...")

# 页脚信息
st.divider()
footer_cols = st.columns([3, 1])
with footer_cols[0]:
    st.caption(f"最后更新: {datetime.now(beijing_tz).strftime('%H:%M:%S')} | 刷新间隔: {st.session_state.refresh_interval}秒")
with footer_cols[1]:
    if st.button("⬆️ 返回顶部", use_container_width=True, key='back_to_top'):
        # 返回顶部通过重新运行实现，清空状态
        st.experimental_rerun()
