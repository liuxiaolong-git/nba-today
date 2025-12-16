import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import time
import concurrent.futures
import json

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
    /* AJAX加载动画 */
    .ajax-loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-left: 10px;
        vertical-align: middle;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .ajax-updated {
        background-color: rgba(144, 238, 144, 0.3);
        transition: background-color 0.5s ease;
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

if 'live_game_ids' not in st.session_state:
    st.session_state.live_game_ids = []

if 'last_ajax_update' not in st.session_state:
    st.session_state.last_ajax_update = {}

if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now(pytz.timezone('Asia/Shanghai')).date()

beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# ====== JavaScript实现局部刷新 ======
st.markdown("""
<script>
// 存储游戏状态和时钟
let gameStates = {};

// AJAX局部刷新函数
async function refreshLiveGames() {
    const liveGameElements = document.querySelectorAll('.live-game[data-game-id]');
    const gameIds = Array.from(liveGameElements).map(el => el.getAttribute('data-game-id'));
    
    if (gameIds.length === 0) return;
    
    // 显示加载状态
    gameIds.forEach(id => {
        const loadingEl = document.getElementById(`loading-${id}`);
        if (loadingEl) {
            loadingEl.style.display = 'inline-block';
        }
    });
    
    try {
        // 调用Streamlit后端API获取实时数据
        const response = await fetch('/_stcore/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event: 'refresh_live_games',
                game_ids: gameIds
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // 更新每个游戏的数据
            for (const gameId in data) {
                const gameData = data[gameId];
                updateGameElement(gameId, gameData);
                
                // 显示更新提示
                const gameElement = document.querySelector(`[data-game-id="${gameId}"]`);
                if (gameElement) {
                    gameElement.classList.add('ajax-updated');
                    setTimeout(() => {
                        gameElement.classList.remove('ajax-updated');
                    }, 1000);
                }
            }
        }
    } catch (error) {
        console.error('刷新失败:', error);
    } finally {
        // 隐藏加载状态
        gameIds.forEach(id => {
            const loadingEl = document.getElementById(`loading-${id}`);
            if (loadingEl) {
                loadingEl.style.display = 'none';
            }
        });
    }
}

// 更新游戏元素
function updateGameElement(gameId, gameData) {
    // 更新比分
    const awayScoreEl = document.getElementById(`score-away-${gameId}`);
    const homeScoreEl = document.getElementById(`score-home-${gameId}`);
    
    if (awayScoreEl && gameData.away_score !== undefined) {
        awayScoreEl.textContent = gameData.away_score;
    }
    if (homeScoreEl && gameData.home_score !== undefined) {
        homeScoreEl.textContent = gameData.home_score;
    }
    
    // 更新节次信息
    const periodEl = document.getElementById(`period-${gameId}`);
    const clockEl = document.getElementById(`clock-${gameId}`);
    
    if (periodEl && gameData.period_text) {
        periodEl.textContent = gameData.period_text;
    }
    if (clockEl && gameData.clock) {
        clockEl.textContent = gameData.clock;
        
        // 更新时钟倒计时
        if (gameData.clock_seconds) {
            const secondsEl = document.getElementById(`clock-seconds-${gameId}`);
            if (secondsEl) {
                secondsEl.setAttribute('data-seconds', gameData.clock_seconds);
            }
        }
    }
    
    // 更新节次比分
    if (gameData.quarter_scores && gameData.quarter_scores.length > 0) {
        const scoresContainer = document.getElementById(`scores-${gameId}`);
        if (scoresContainer) {
            scoresContainer.innerHTML = '';
            gameData.quarter_scores.forEach(quarter => {
                const quarterEl = document.createElement('span');
                quarterEl.className = 'quarter-score';
                quarterEl.innerHTML = `<strong>${quarter.quarter}</strong><br>${quarter.away_score}-${quarter.home_score}`;
                scoresContainer.appendChild(quarterEl);
            });
        }
    }
}

// 时钟倒计时函数
function updateClocks() {
    const clockElements = document.querySelectorAll('[id^="clock-"]');
    clockElements.forEach(clockEl => {
        const gameId = clockEl.id.replace('clock-', '');
        const secondsEl = document.getElementById(`clock-seconds-${gameId}`);
        
        if (secondsEl) {
            let seconds = parseInt(secondsEl.getAttribute('data-seconds'));
            if (seconds > 0) {
                seconds--;
                secondsEl.setAttribute('data-seconds', seconds);
                
                const minutes = Math.floor(seconds / 60);
                const secs = seconds % 60;
                clockEl.textContent = `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
            } else if (seconds === 0) {
                clockEl.textContent = "0:00";
                // 时钟到0时触发刷新
                refreshLiveGames();
            }
        }
    });
}

// 页面刷新倒计时
let pageRefreshCountdown = 0;
let pageRefreshInterval = 30;

function updatePageRefreshCountdown() {
    const refreshCountdownEl = document.getElementById('refresh-countdown');
    if (refreshCountdownEl) {
        if (pageRefreshCountdown > 0) {
            pageRefreshCountdown--;
            refreshCountdownEl.textContent = `${pageRefreshCountdown}秒`;
            if (pageRefreshCountdown <= 5) {
                refreshCountdownEl.classList.add('pulse-animation');
            } else {
                refreshCountdownEl.classList.remove('pulse-animation');
            }
        } else if (pageRefreshCountdown <= 0) {
            // 重置倒计时
            pageRefreshCountdown = pageRefreshInterval;
            // 执行局部刷新而不是整个页面刷新
            refreshLiveGames();
        }
    }
}

// 设置自动刷新
let autoRefresh = true;

// 初始化函数
function initAutoRefresh() {
    // 从页面元素获取设置
    const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
    const refreshIntervalSelect = document.getElementById('refresh-interval-select');
    
    if (autoRefreshToggle) {
        autoRefresh = autoRefreshToggle.checked;
    }
    
    if (refreshIntervalSelect) {
        pageRefreshInterval = parseInt(refreshIntervalSelect.value);
        pageRefreshCountdown = pageRefreshInterval;
    }
    
    // 每秒更新一次时钟
    setInterval(updateClocks, 1000);
    
    // 每秒更新一次页面刷新倒计时
    if (autoRefresh) {
        setInterval(updatePageRefreshCountdown, 1000);
    }
    
    // 每10秒刷新一次进行中的比赛
    setInterval(refreshLiveGames, 10000);
    
    // 初始刷新
    setTimeout(refreshLiveGames, 2000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化以确保所有元素都已加载
    setTimeout(initAutoRefresh, 1000);
    
    // 监听自动刷新开关变化
    const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('change', function() {
            autoRefresh = this.checked;
            if (autoRefresh) {
                pageRefreshCountdown = pageRefreshInterval;
            }
        });
    }
    
    // 监听刷新间隔变化
    const refreshIntervalSelect = document.getElementById('refresh-interval-select');
    if (refreshIntervalSelect) {
        refreshIntervalSelect.addEventListener('change', function() {
            pageRefreshInterval = parseInt(this.value);
            pageRefreshCountdown = pageRefreshInterval;
        });
    }
});
</script>
""", unsafe_allow_html=True)

# ====== 翻译数据加载 ======
@st.cache_resource(ttl=600)
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
@st.cache_data(ttl=15, show_spinner=False)
def fetch_nba_schedule(date_str):
    """获取赛程数据，缓存时间较长"""
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

@st.cache_data(ttl=5, show_spinner=False)  # 短缓存，用于实时数据
def fetch_live_game_data(game_id):
    """获取单个进行中比赛的数据，缓存时间很短"""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': game_id}, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            
            # 从摘要数据中提取比赛信息
            competitions = data.get('header', {}).get('competitions', [{}])
            if competitions:
                competition = competitions[0]
                status = competition.get('status', {})
                
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
                
                # 获取比分
                competitors = competition.get('competitors', [])
                away_score = 0
                home_score = 0
                quarter_scores = []
                
                if len(competitors) >= 2:
                    away_competitor = competitors[0]
                    home_competitor = competitors[1]
                    
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
                        
                        quarter_num = i + 1
                        if quarter_num <= 4:
                            quarter_label = f"第{quarter_num}节"
                        else:
                            quarter_label = f"加时{quarter_num-4}"
                        
                        quarter_scores.append({
                            'quarter': quarter_label,
                            'away_score': away_q_score,
                            'home_score': home_q_score
                        })
                
                # 生成状态文本
                if period <= 4:
                    period_text = f"第{period}节"
                else:
                    period_text = f"加时{period-4}"
                
                return {
                    'period': period,
                    'clock': clock,
                    'clock_seconds': clock_seconds,
                    'period_text': period_text,
                    'quarter_scores': quarter_scores,
                    'away_score': away_score,
                    'home_score': home_score
                }
    except Exception:
        pass
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

# ====== AJAX端点处理 ======
def handle_ajax_request():
    """处理AJAX请求，返回实时比赛数据"""
    try:
        # 这里应该从请求中获取数据，但Streamlit不支持直接访问请求
        # 所以我们通过session_state来传递
        if 'ajax_game_ids' in st.session_state:
            game_ids = st.session_state.ajax_game_ids
            live_data = {}
            
            for game_id in game_ids:
                game_data = fetch_live_game_data(game_id)
                if game_data:
                    live_data[game_id] = game_data
            
            return live_data
    except Exception:
        pass
    return {}

# ====== 主界面 ======
col1, col2 = st.columns([3, 1])
with col1:
    selected_date = st.date_input(
        "选择日期",
        value=st.session_state.selected_date,
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3),
        label_visibility="collapsed",
        key='date_selector'
    )
    
    # 更新选中的日期
    if selected_date != st.session_state.selected_date:
        st.session_state.selected_date = selected_date
        st.cache_data.clear()
        st.rerun()

with col2:
    manual_refresh = st.button("🔄 刷新", use_container_width=True, key='manual_refresh_top')
    if manual_refresh:
        st.session_state.last_refresh_time = time.time()
        st.cache_data.clear()
        st.rerun()

st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')}")

# 加载主赛程数据
with st.spinner("加载赛程数据..."):
    schedule = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule or 'events' not in schedule:
    st.error("无法获取数据，请稍后重试")
    st.stop()

events = schedule['events']
if not events:
    st.info("今日无比赛")
    st.stop()

# 识别进行中的比赛
live_game_ids = []
for event in events:
    status_type = event.get('status', {}).get('type', {})
    if status_type.get('state', 'pre') == 'in':
        live_game_ids.append(event['id'])

st.session_state.live_game_ids = live_game_ids

# 并行加载球员数据（只加载进行中和已结束的比赛）
live_or_post_event_ids = []
for event in events:
    status_type = event.get('status', {}).get('type', {})
    if status_type.get('state', 'pre') in ['in', 'post']:
        live_or_post_event_ids.append(event['id'])

player_stats_map = {}
if live_or_post_event_ids:
    with st.spinner("加载球员数据..."):
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
    
    # 获取初始比分
    home_score = home.get('score', '0')
    away_score = away.get('score', '0')

    status_type = event.get('status', {}).get('type', {})
    state = status_type.get('state', 'pre')
    desc = status_type.get('description', '未开始')
    
    if state == 'in':
        status_badge, game_class = "🟢 直播中", "live-game"
        # 获取实时数据
        live_data = fetch_live_game_data(event['id'])
        if live_data:
            home_score = live_data['home_score']
            away_score = live_data['away_score']
    elif state == 'post':
        status_badge, game_class = "⚫ 已结束", "finished-game"
    else:
        status_badge, game_class = "⏳ 未开始", "upcoming-game"

    try:
        utc_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
        bj_time = utc_time.astimezone(beijing_tz).strftime("%H:%M")
    except:
        bj_time = "时间待定"

    # 比赛卡片 - 添加data-game-id属性用于JavaScript识别
    game_card_html = f'<div class="game-card {game_class}" data-game-id="{event["id"]}">'
    st.markdown(game_card_html, unsafe_allow_html=True)
    
    # 比赛基本信息
    cols = st.columns([2, 1, 2])
    with cols[0]:
        st.markdown(f'<div class="team-name">{away_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<span id="score-away-{event["id"]}" style="font-size: 24px; font-weight: bold;">{away_score}</span>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown("**VS**")
        st.markdown(f'<div class="game-time">{bj_time}</div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="team-name">{home_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<span id="score-home-{event["id"]}" style="font-size: 24px; font-weight: bold;">{home_score}</span>', unsafe_allow_html=True)
    
    # 显示状态信息
    if state == 'in':
        # 直播中：显示节次和倒计时
        live_data = fetch_live_game_data(event['id'])
        if live_data:
            period_text = live_data['period_text']
            clock = live_data['clock']
            clock_seconds = live_data['clock_seconds']
            
            # 添加时钟倒计时的隐藏数据存储
            st.markdown(f'<div id="clock-seconds-{event["id"]}" data-seconds="{clock_seconds}" style="display:none;"></div>', unsafe_allow_html=True)
            
            st.markdown(f"**{status_badge} {desc}**")
            st.markdown(f"**🎯 <span id='period-{event[\"id\"]}'>{period_text}</span> ⏱️ <span id='clock-{event[\"id\"]}'>{clock}</span>**")
            
            # 显示每节得分
            if live_data['quarter_scores']:
                st.markdown("**每节比分:**")
                
                # 创建容器用于JavaScript更新
                scores_container = st.empty()
                with scores_container.container():
                    cols = st.columns(min(4, len(live_data['quarter_scores'])))
                    for idx, q in enumerate(live_data['quarter_scores']):
                        if idx < 4:
                            col_idx = idx % len(cols)
                            with cols[col_idx]:
                                st.markdown(
                                    f"<div class='quarter-score'>"
                                    f"<strong>{q['quarter']}</strong><br>"
                                    f"{q['away_score']}-{q['home_score']}"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )
                
                # 添加用于JavaScript更新的容器
                st.markdown(f'<div id="scores-{event["id"]}" style="display:none;"></div>', unsafe_allow_html=True)
                
                st.markdown(f"**当前总分: {away_name} {away_score}-{home_score} {home_name}**")
            
            # 添加AJAX加载指示器
            st.markdown(f'<div id="loading-{event["id"]}" class="ajax-loading" style="display:none;"></div>', unsafe_allow_html=True)
        
    elif state == 'post':
        # 已结束：显示最终信息
        st.markdown(f"**{status_badge} {desc}**")
        game_data = player_stats_map.get(event['id'])
        if game_data:
            # 显示节次比分
            competitions = game_data.get('header', {}).get('competitions', [{}])
            if competitions:
                competition = competitions[0]
                competitors = competition.get('competitors', [])
                if len(competitors) >= 2:
                    away_linescores = competitors[0].get('linescores', [])
                    home_linescores = competitors[1].get('linescores', [])
                    
                    if away_linescores and home_linescores:
                        st.markdown("**全场比分:**")
                        quarter_cols = st.columns(min(4, len(away_linescores)))
                        
                        for idx in range(len(away_linescores)):
                            quarter_num = idx + 1
                            if quarter_num <= 4:
                                quarter_label = f"第{quarter_num}节"
                            else:
                                quarter_label = f"加时{quarter_num-4}"
                            
                            col_idx = idx % len(quarter_cols)
                            with quarter_cols[col_idx]:
                                st.markdown(
                                    f"<div class='quarter-score'>"
                                    f"<strong>{quarter_label}</strong><br>"
                                    f"{away_linescores[idx].get('value', 0)}-{home_linescores[idx].get('value', 0)}"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )
    else:
        # 未开始
        st.markdown(f"**{status_badge} {desc}**")
    
    # 球员数据（只在初始加载时渲染，不通过AJAX更新）
    if state in ['in', 'post']:
        game_data = player_stats_map.get(event['id'])
        if game_data:
            # 简化球员数据显示
            st.markdown("---")
            st.markdown("**球员数据**")
            
            # 使用session_state管理展开状态
            game_key = f"game_{event['id']}"
            if game_key not in st.session_state.expanded_games:
                st.session_state.expanded_games[game_key] = False
            
            # 只显示简要数据，详细数据通过按钮展开
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"👤 {away_name} 球员", key=f"away_{event['id']}", use_container_width=True):
                    st.session_state.expanded_games[game_key] = not st.session_state.expanded_games[game_key]
            
            with col2:
                if st.button(f"👤 {home_name} 球员", key=f"home_{event['id']}", use_container_width=True):
                    st.session_state.expanded_games[game_key] = not st.session_state.expanded_games[game_key]
    
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
    
    # 添加HTML元素供JavaScript读取
    st.markdown(f'<input type="checkbox" id="auto-refresh-toggle" {"checked" if st.session_state.auto_refresh else ""} style="display:none;">', unsafe_allow_html=True)

with col2:
    interval_options = [10, 30, 60, 120]
    refresh_interval = st.selectbox(
        "刷新间隔(秒)",
        options=interval_options,
        index=interval_options.index(st.session_state.refresh_interval) if st.session_state.refresh_interval in interval_options else 1,
        help="设置自动刷新的时间间隔",
        key='refresh_interval_select'
    )
    
    # 添加HTML元素供JavaScript读取
    st.markdown(f'<select id="refresh-interval-select" style="display:none;"><option value="{refresh_interval}">{refresh_interval}</option></select>', unsafe_allow_html=True)

with col3:
    # 更新session state
    if st.session_state.auto_refresh != auto_refresh:
        st.session_state.auto_refresh = auto_refresh
    if st.session_state.refresh_interval != refresh_interval:
        st.session_state.refresh_interval = refresh_interval
        st.session_state.last_refresh_time = time.time()
    
    # 显示状态和动态倒计时
    if st.session_state.auto_refresh:
        status_text = f"状态: <span class='auto-refresh-on'>开启</span>"
        countdown_text = f"倒计时: <span class='countdown' id='refresh-countdown'>{st.session_state.refresh_interval}秒</span>"
    else:
        status_text = "状态: <span class='auto-refresh-off'>关闭</span>"
        countdown_text = "倒计时: --"
    
    st.markdown(status_text, unsafe_allow_html=True)
    st.markdown(countdown_text, unsafe_allow_html=True)

# 手动刷新按钮（底部）- 现在只触发局部刷新
if st.button("🔄 立即手动刷新进行中比赛", use_container_width=True, type="primary", key='manual_refresh_bottom'):
    # 将游戏ID存储到session state供JavaScript使用
    st.session_state.ajax_game_ids = st.session_state.live_game_ids
    # 显示刷新提示
    st.toast("正在刷新进行中的比赛...", icon="🔄")

st.markdown('</div>', unsafe_allow_html=True)

# 页脚信息
st.divider()
footer_cols = st.columns([3, 1])
with footer_cols[0]:
    st.caption(f"最后更新: {datetime.now(beijing_tz).strftime('%H:%M:%S')} | 刷新间隔: {st.session_state.refresh_interval}秒 | 进行中比赛: {len(live_game_ids)}场")
with footer_cols[1]:
    if st.button("⬆️ 返回顶部", use_container_width=True, key='back_to_top'):
        st.rerun()

# 添加JavaScript初始化代码
st.markdown("""
<script>
// 页面加载完成后初始化局部刷新
window.addEventListener('load', function() {
    // 延迟执行以确保所有元素都已加载
    setTimeout(function() {
        // 初始化时钟显示
        const clockElements = document.querySelectorAll('[id^="clock-"]');
        clockElements.forEach(clockEl => {
            const gameId = clockEl.id.replace('clock-', '');
            const secondsEl = document.getElementById('clock-seconds-' + gameId);
            if (secondsEl) {
                let seconds = parseInt(secondsEl.getAttribute('data-seconds'));
                const minutes = Math.floor(seconds / 60);
                const secs = seconds % 60;
                clockEl.textContent = `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
            }
        });
        
        // 如果有进行中的比赛，开始定时刷新
        const liveGames = document.querySelectorAll('.live-game[data-game-id]');
        if (liveGames.length > 0) {
            // 每10秒刷新一次进行中的比赛
            setInterval(function() {
                refreshLiveGames();
            }, 10000);
            
            // 初始刷新
            setTimeout(refreshLiveGames, 2000);
        }
    }, 1500);
});
</script>
""", unsafe_allow_html=True)
