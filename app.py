import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import time
import concurrent.futures

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
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem !important; }
        .game-card {
            background: white; border-radius: 10px; padding: 12px; margin: 8px 0;
            border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .simple-table-container, .full-table-container {
            overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 8px 0;
        }
        .full-table-container { border-radius: 8px; border: 1px solid #e0e0e0; }
        .dataframe { font-size: 12px !important; }
        .dataframe th, .dataframe td { padding: 6px 4px !important; white-space: nowrap; }
        .stButton > button { min-height: 40px; font-size: 14px; width: 100%; }
        .refresh-panel {
            background-color: #f8f9fa; border-radius: 10px; padding: 10px;
            margin-top: 10px; border: 1px solid #dee2e6;
        }
        h1 { font-size: 20px !important; margin-bottom: 12px !important; }
        h2, h3 { font-size: 16px !important; }
        .team-name {
            font-size: 14px; font-weight: bold; white-space: nowrap;
            overflow: hidden; text-overflow: ellipsis; max-width: 120px;
        }
        .game-time { font-size: 12px; color: #666; }
        .countdown { font-weight: bold; color: #2196F3; font-size: 13px; }
        .auto-refresh-on { color: #4CAF50; font-weight: bold; }
        .auto-refresh-off { color: #9E9E9E; }
        .period-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 6px 12px; border-radius: 20px;
            font-size: 12px; display: inline-block; margin: 4px 0;
        }
        .quarter-score {
            background: #f0f2f6;
            padding: 4px 8px;
            border-radius: 10px;
            font-size: 11px;
            margin: 2px;
            display: inline-block;
        }
    }
    .live-game { border-left: 4px solid #4CAF50 !important; }
    .finished-game { border-left: 4px solid #9E9E9E !important; }
    .upcoming-game { border-left: 4px solid #2196F3 !important; }
    /* 动态倒计时动画 */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .pulse-animation {
        animation: pulse 1s infinite;
        display: inline-block;
    }
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        margin-right: 8px;
        background: #e8f5e9;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏀 NBA实时赛程(小包子)")

# ====== 初始化状态 ======
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
    
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30
    
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = time.time()

if 'untranslated_players' not in st.session_state:
    st.session_state.untranslated_players = set()

if 'expanded_games' not in st.session_state:
    st.session_state.expanded_games = {}

if 'game_period_info' not in st.session_state:
    st.session_state.game_period_info = {}

if 'countdown_times' not in st.session_state:
    st.session_state.countdown_times = {}

beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# ====== 简化JavaScript动态倒计时 ======
st.markdown("""
<script>
// 更新页面刷新倒计时
function updateRefreshCountdown() {
    const refreshCountdownEl = document.getElementById('refresh-countdown');
    if (refreshCountdownEl) {
        let seconds = parseInt(refreshCountdownEl.getAttribute('data-seconds'));
        if (seconds > 0) {
            seconds--;
            refreshCountdownEl.setAttribute('data-seconds', seconds);
            refreshCountdownEl.textContent = `${seconds}秒`;
            if (seconds <= 5) {
                refreshCountdownEl.classList.add('pulse-animation');
            } else {
                refreshCountdownEl.classList.remove('pulse-animation');
            }
        } else if (seconds <= 0) {
            // 当倒计时为0时，重新加载页面
            window.location.reload();
        }
    }
}

// 每秒更新一次
setInterval(updateRefreshCountdown, 100000);

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    updateRefreshCountdown();
});
</script>
""", unsafe_allow_html=True)

# ====== 翻译数据加载 ======
@st.cache_resource(ttl=600000)
def get_translations():
    try:
        from translations import TEAM_TRANSLATION, PLAYER_TRANSLATION
        return TEAM_TRANSLATION, PLAYER_TRANSLATION
    except ImportError:
        return {}, {}

_team_translation, _player_translation = get_translations()

def translate_team_name(name):
    return _team_translation.get(name, name)

def translate_player_name(name):
    if not name:
        return name
    name = name.strip()
    if name in _player_translation:
        return _player_translation[name]
    
    name_parts = name.split()
    if len(name_parts) > 1:
        suffixes = ['Jr.', 'Jr', 'Sr.', 'Sr', 'II', 'III', 'IV', 'V']
        if name_parts[-1] in suffixes:
            base_name = ' '.join(name_parts[:-1])
            if base_name in _player_translation:
                translated = _player_translation[base_name]
                suffix_map = {'Jr.':'小','Jr':'小','Sr.':'老','Sr':'老','II':'二世','III':'三世','IV':'四世','V':'五世'}
                return f"{translated}{suffix_map.get(name_parts[-1], '')}"
    
    if name and name not in ['DNP', 'N/A', '--', '', 'null', 'None']:
        st.session_state.untranslated_players.add(name)
    return name

# ====== API 数据获取函数 ======
@st.cache_data(ttl=10, show_spinner=False)  # 缩短缓存时间，加快实时数据更新
def fetch_nba_schedule(date_str):
    try:
        eastern = pytz.timezone('America/New_York')
        beijing_dt = beijing_tz.localize(datetime.strptime(date_str, '%Y-%m-%d'))
        eastern_dt = beijing_dt.astimezone(eastern)
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        params = {'dates': eastern_dt.strftime('%Y%m%d'), 'lang': 'zh', 'region': 'cn'}
        resp = requests.get(url, params=params, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

def fetch_single_player_stats(event_id):
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return event_id, data
    except Exception:
        pass
    return event_id, None

def fetch_all_player_stats_parallel(event_ids):
    player_stats_map = {}
    if event_ids:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(event_ids))) as executor:
            future_to_id = {executor.submit(fetch_single_player_stats, eid): eid for eid in event_ids}
            for future in concurrent.futures.as_completed(future_to_id):
                event_id, data = future.result()
                if data:
                    player_stats_map[event_id] = data
    return player_stats_map

# ====== 获取比赛节次信息 ======
def get_game_period_info(event):
    """从事件数据中提取节次信息"""
    try:
        competitions = event.get('competitions', [{}])
        if not competitions:
            return None
            
        competition = competitions[0]
        status = competition.get('status', {})
        status_type = status.get('type', {})
        
        # 获取节次和时钟
        period = status.get('period', 0)
        clock = status.get('displayClock', '')
        
        # 将时钟转换为秒数
        clock_seconds = 0
        if clock and clock != '0:00' and clock != '0':
            if ':' in clock:
                try:
                    minutes, seconds = clock.split(':')
                    clock_seconds = int(minutes) * 60 + int(seconds)
                except:
                    clock_seconds = 0
            else:
                try:
                    clock_seconds = int(clock)
                except:
                    clock_seconds = 0
        
        # 处理比赛状态文本
        state = status_type.get('state', 'pre')
        description = status_type.get('description', '')
        
        # 获取比分
        competitors = competition.get('competitors', [])
        away_score = 0
        home_score = 0
        quarter_scores = []
        
        if len(competitors) >= 2:
            away_competitor = competitors[0]
            home_competitor = competitors[1]
            
            # 获取总分
            away_score = away_competitor.get('score', '0')
            home_score = home_competitor.get('score', '0')
            
            # 获取每节得分
            away_linescores = away_competitor.get('linescores', [])
            home_linescores = home_competitor.get('linescores', [])
            
            # 格式化每节得分
            quarter_scores = []
            for i in range(min(len(away_linescores), len(home_linescores))):
                away_q_score = away_linescores[i].get('value', 0)
                home_q_score = home_linescores[i].get('value', 0)
                
                # 处理加时赛显示
                quarter_num = i + 1
                if quarter_num <= 4:
                    quarter_label = f"第{quarter_num}节"
                else:
                    quarter_label = f"加时{quarter_num-4}"
                
                quarter_scores.append({
                    'quarter': quarter_label,
                    'away_score': away_q_score,
                    'home_score': home_q_score,
                    'quarter_num': quarter_num
                })
        
        # 生成状态文本
        if state == 'in':
            if period <= 4:
                period_text = f"第{period}节"
            else:
                period_text = f"加时{period-4}"
        elif state == 'post':
            period_text = "比赛结束"
        else:
            period_text = "未开始"
        
        return {
            'period': period,
            'clock': clock,
            'clock_seconds': clock_seconds,
            'period_text': period_text,
            'quarter_scores': quarter_scores,
            'state': state,
            'description': description,
            'away_score': away_score,
            'home_score': home_score
        }
    except Exception as e:
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
                    if (safe_int(player_data['得分']) > 0 or safe_int(player_data['篮板']) > 0 or 
                        safe_int(player_data['助攻']) > 0 or player_data['时间'] not in ('0:00', '0')):
                        parsed.append(player_data)
                except Exception:
                    continue
            return parsed
        away_data = extract_team_data(away_players)
        home_data = extract_team_data(home_players)
        return away_data, home_data
    except Exception as e:
        return [], []

def display_simple_table(players_data, team_name):
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

# ====== 主界面 ======
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
    manual_refresh = st.button("🔄 刷新", use_container_width=True, key='manual_refresh_top')
    if manual_refresh:
        st.session_state.last_refresh_time = time.time()
        st.cache_data.clear()
        st.rerun()

# 计算倒计时
current_time = time.time()
time_since_last_refresh = current_time - st.session_state.last_refresh_time
countdown_seconds = max(0, st.session_state.refresh_interval - int(time_since_last_refresh))

# 检查是否需要自动刷新
if st.session_state.auto_refresh and countdown_seconds <= 0:
    st.session_state.last_refresh_time = current_time
    st.cache_data.clear()
    st.rerun()

st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')}")

# 加载主赛程数据
with st.spinner("快速加载赛程..."):
    schedule = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule or 'events' not in schedule:
    st.error("无法获取数据，请稍后重试")
    st.stop()

events = schedule['events']
if not events:
    st.info("今日无比赛")
    st.stop()

# 并行加载球员数据
live_or_post_event_ids = []
for event in events:
    status_type = event.get('status', {}).get('type', {})
    if status_type.get('state', 'pre') in ['in', 'post']:
        live_or_post_event_ids.append(event['id'])

player_stats_map = {}
if live_or_post_event_ids:
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
    
    # 获取节次信息
    period_info = get_game_period_info(event)
    if period_info:
        home_score = period_info['home_score']
        away_score = period_info['away_score']
        st.session_state.game_period_info[event['id']] = period_info
    else:
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
    
    # 比赛基本信息
    cols = st.columns([2, 1, 2])
    with cols[0]:
        st.markdown(f'<div class="team-name">{away_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<span style="font-size: 24px; font-weight: bold;">{away_score}</span>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown("**VS**")
        st.markdown(f'<div class="game-time">{bj_time}</div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="team-name">{home_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<span style="font-size: 24px; font-weight: bold;">{home_score}</span>', unsafe_allow_html=True)
    
    # 显示状态信息
    st.markdown(f"**{status_badge} {desc}**")
    
    # 如果是直播中或已结束的比赛，显示节次信息
    if state in ['in', 'post'] and period_info:
        if period_info['state'] == 'in':
            # 直播中：显示节次和倒计时
            clock_display = ""
            if period_info['clock'] and period_info['clock'] != '0:00':
                clock_display = f"⏱️ {period_info['clock']}"
                
            # 修复语法错误：使用单引号包围整个字符串
            period_display = f"**🎯 {period_info['period_text']} {clock_display}**"
            st.markdown(period_display)
            
            # 显示每节得分
            if period_info['quarter_scores']:
                st.markdown("**每节比分:**")
                
                # 创建列来显示节次比分
                quarter_cols = st.columns(min(4, len(period_info['quarter_scores'])))
                
                for idx, q in enumerate(period_info['quarter_scores']):
                    if idx < 4:  # 最多显示4列
                        col_idx = idx % len(quarter_cols)
                        with quarter_cols[col_idx]:
                            st.markdown(
                                f"<div style='background: #f0f2f6; padding: 4px 8px; border-radius: 10px; "
                                f"font-size: 11px; margin: 2px;'>"
                                f"**{q['quarter']}**<br>"
                                f"{q['away_score']}-{q['home_score']}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                
                st.markdown(f"**当前总分: {away_name} {away_score}-{home_score} {home_name}**")
        
        elif period_info['state'] == 'post':
            # 已结束：显示最终节次信息
            st.markdown(f"**🏁 {period_info['period_text']}**")
            
            # 显示所有节次得分
            if period_info['quarter_scores']:
                st.markdown("**全场比分:**")
                
                # 创建列来显示节次比分
                quarter_cols = st.columns(min(4, len(period_info['quarter_scores'])))
                
                for idx, q in enumerate(period_info['quarter_scores']):
                    if idx < 8:  # 最多显示8节（4节+4个加时）
                        col_idx = idx % len(quarter_cols)
                        with quarter_cols[col_idx]:
                            st.markdown(
                                f"<div style='background: #f0f2f6; padding: 4px 8px; border-radius: 10px; "
                                f"font-size: 11px; margin: 2px;'>"
                                f"**{q['quarter']}**<br>"
                                f"{q['away_score']}-{q['home_score']}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                
                st.markdown(f"**总比分: {away_name} {away_score}-{home_score} {home_name}**")
    
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
                        col_btn1, _ = st.columns([1, 1])
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
                        col_btn1, _ = st.columns([1, 1])
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

# ====== 自动刷新控制面板 ======
st.markdown("---")
st.markdown('<div class="refresh-panel">', unsafe_allow_html=True)
st.markdown("### 🔄 自动刷新控制")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    auto_refresh = st.toggle(
        "自动刷新", 
        value=st.session_state.auto_refresh,
        help="开启后页面会自动定期刷新",
        key='auto_refresh_toggle'
    )
with col2:
    interval_options = [100, 300, 600, 1200]
    refresh_interval = st.selectbox(
        "刷新间隔(秒)",
        options=interval_options,
        index=interval_options.index(st.session_state.refresh_interval) if st.session_state.refresh_interval in interval_options else 1,
        help="设置自动刷新的时间间隔",
        key='refresh_interval_select'
    )
with col3:
    # 更新session state
    if st.session_state.auto_refresh != auto_refresh:
        st.session_state.auto_refresh = auto_refresh
    if st.session_state.refresh_interval != refresh_interval:
        st.session_state.refresh_interval = refresh_interval
        st.session_state.last_refresh_time = current_time
    
    # 显示状态和动态倒计时
    if st.session_state.auto_refresh:
        status_text = f"状态: <span class='auto-refresh-on'>开启</span>"
        # 使用JavaScript实现动态倒计时
        countdown_text = f"倒计时: <span class='countdown pulse-animation' id='refresh-countdown' data-seconds='{countdown_seconds}'>{countdown_seconds}秒</span>"
    else:
        status_text = "状态: <span class='auto-refresh-off'>关闭</span>"
        countdown_text = "倒计时: --"
    
    st.markdown(status_text, unsafe_allow_html=True)
    st.markdown(countdown_text, unsafe_allow_html=True)

# 手动刷新按钮（底部）
if st.button("🔄 立即手动刷新", use_container_width=True, type="primary", key='manual_refresh_bottom'):
    st.session_state.last_refresh_time = time.time()
    st.cache_data.clear()
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ====== 自动刷新机制 ======
if st.session_state.auto_refresh:
    refresh_seconds = st.session_state.refresh_interval + 1
    # 使用Streamlit的自动刷新功能
    st.markdown(f"""
    <meta http-equiv="refresh" content="{refresh_seconds}">
    """, unsafe_allow_html=True)

# 页脚信息
st.divider()
footer_cols = st.columns([3, 1])
with footer_cols[0]:
    st.caption(f"最后更新: {datetime.now(beijing_tz).strftime('%H:%M:%S')} | 刷新间隔: {st.session_state.refresh_interval}秒")
with footer_cols[1]:
    if st.button("⬆️ 返回顶部", use_container_width=True, key='back_to_top'):
        st.rerun()


