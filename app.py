import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta

# 移动端优化配置
st.set_page_config(
    page_title="NBA赛程查询(李菲同学)", 
    page_icon="🏀", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 移动端优化的CSS
st.markdown("""
<style>
    /* 移动端适配 */
    @media (max-width: 768px) {
        /* 主容器调整 */
        .main .block-container {
            padding: 0.5rem !important;
        }
        
        /* 比赛卡片 */
        .game-card {
            background: white;
            border-radius: 10px;
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* 简化表格 - 默认只显示三列 */
        .simple-table {
            width: 100%;
            font-size: 13px;
        }
        
        .simple-table th, .simple-table td {
            padding: 6px 4px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .simple-table th {
            font-weight: bold;
            color: #666;
            background-color: #f8f9fa;
        }
        
        /* 完整表格容器 - 水平滚动 */
        .full-table-container {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin: 8px 0;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        /* 完整表格 */
        .dataframe {
            font-size: 12px !important;
            min-width: 700px;
        }
        
        .dataframe th, .dataframe td {
            padding: 6px 4px !important;
            white-space: nowrap;
        }
        
        /* 按钮优化 */
        .stButton > button {
            min-height: 40px;
            font-size: 14px;
            width: 100%;
        }
        
        /* 列布局 */
        .stColumn {
            padding: 4px !important;
        }
        
        /* 标题大小 */
        h1 {
            font-size: 20px !important;
            margin-bottom: 12px !important;
        }
        
        h2, h3 {
            font-size: 16px !important;
        }
        
        .stSubheader {
            font-size: 14px !important;
        }
        
        /* 状态标签 */
        .status-badge {
            font-size: 11px;
            padding: 2px 6px;
            border-radius: 10px;
            display: inline-block;
            margin-right: 4px;
            background-color: #f0f0f0;
        }
        
        /* 球队名称 */
        .team-name {
            font-size: 14px;
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 120px;
        }
        
        /* 比赛时间 */
        .game-time {
            font-size: 12px;
            color: #666;
        }
        
        /* 展开详细数据按钮 */
        .detail-btn {
            font-size: 12px !important;
            padding: 4px 10px !important;
            margin: 4px 0 !important;
            width: auto !important;
        }
        
        /* 分隔线 */
        .stDivider {
            margin: 12px 0 !important;
        }
        
        /* 侧边栏 */
        section[data-testid="stSidebar"] {
            min-width: 200px;
            max-width: 85vw;
        }
        
        /* 展开器 */
        .streamlit-expanderHeader {
            font-size: 14px !important;
            padding: 8px 0 !important;
        }
    }
    
    /* 通用优化 */
    .mobile-friendly {
        touch-action: manipulation;
    }
    
    /* 直播比赛指示器 */
    .live-game {
        border-left: 4px solid #4CAF50 !important;
    }
    
    /* 已结束比赛 */
    .finished-game {
        border-left: 4px solid #9E9E9E !important;
    }
    
    /* 未开始比赛 */
    .upcoming-game {
        border-left: 4px solid #2196F3 !important;
    }
    
    /* 得分高亮 */
    .high-score {
        font-weight: bold;
        color: #e53935;
    }
    
    /* 表格列宽调整 */
    .simple-table th:nth-child(1) { width: 50%; } /* 球员 */
    .simple-table th:nth-child(2) { width: 25%; } /* 时间 */
    .simple-table th:nth-child(3) { width: 25%; } /* 得分 */
</style>
""", unsafe_allow_html=True)

st.title("🏀 NBA实时赛程(小包子)")

# 初始化 session state
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0
    
if 'untranslated_players' not in st.session_state:
    st.session_state.untranslated_players = set()

# 初始化每个比赛的展开状态
if 'expanded_games' not in st.session_state:
    st.session_state.expanded_games = {}

beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# ====== 从配置文件加载翻译数据 ======
@st.cache_data(ttl=2592000)
def load_translations():
    """加载球队和球员翻译数据"""
    try:
        from translations import TEAM_TRANSLATION, PLAYER_TRANSLATION
        return TEAM_TRANSLATION, PLAYER_TRANSLATION
    except ImportError:
        st.warning("⚠️ 未找到翻译配置文件")
        return {}, {}

team_translation, player_translation = load_translations()

def translate_team_name(name):
    """翻译球队名称"""
    return team_translation.get(name, name)

def translate_player_name(name):
    """翻译球员名称"""
    if not name:
        return name
    
    name = name.strip()
    
    if name in player_translation:
        return player_translation[name]
    
    # 处理后缀
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
    
    # 尝试标准化匹配
    normalized = name.replace('.', '')
    if normalized in player_translation:
        return player_translation[normalized]
    
    # 模糊匹配
    for eng_name, chi_name in player_translation.items():
        if eng_name.lower() == name.lower():
            return chi_name
    
    # 记录未翻译的名称
    invalid_names = ['DNP', 'N/A', '--', '', 'null', 'None']
    if name not in invalid_names:
        st.session_state.untranslated_players.add(name)
    
    return name

# ====== API 数据获取函数 ======
@st.cache_data(ttl=30)
def fetch_nba_schedule(date_str):
    """获取NBA赛程"""
    try:
        eastern = pytz.timezone('America/New_York')
        beijing_dt = beijing_tz.localize(datetime.strptime(date_str, '%Y-%m-%d'))
        eastern_dt = beijing_dt.astimezone(eastern)
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        params = {'dates': eastern_dt.strftime('%Y%m%d'), 'lang': 'zh', 'region': 'cn'}
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"获取赛程失败: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_player_stats(event_id):
    """获取球员统计数据"""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, 
                          headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'}, 
                          timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return data
        
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/boxscore?event={event_id}"
        resp = requests.get(url, 
                          headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'}, 
                          timeout=10)
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
    """解析球员统计数据 - 保持原始列结构"""
    try:
        if not game_data or 'boxscore' not in game_data:
            return [], []
            
        players_section = game_data.get('boxscore', {}).get('players', [])
        if not players_section or len(players_section) < 2:
            return [], []

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
                    if not name_en or name_en in ['DNP', 'N/A', '--', 'null', 'None']:
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
                            stat_map[label] = str(value).strip() if value else ''
                    
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
                    
                    # 创建球员数据字典 - 保持原始列结构
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

# ====== 简化的表格显示函数 ======
def display_simple_table(players_data, team_name):
    """显示简化的表格（只显示球员、时间、得分）"""
    if not players_data:
        st.info("暂无球员数据")
        return
    
    # 按得分排序
    players_data = sorted(players_data, key=lambda x: safe_int(x['得分'], 0), reverse=True)
    
    # 只取前10名球员（移动端节省空间）
    players_data = players_data[:10]
    
    # 创建简化的HTML表格
    html = f"""
    <div class="simple-table">
        <table style="width:100%">
            <thead>
                <tr>
                    <th>球员</th>
                    <th>时间</th>
                    <th>得分</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for player in players_data:
        score_class = "high-score" if safe_int(player['得分'], 0) >= 20 else ""
        html += f"""
            <tr>
                <td>{player['球员']}</td>
                <td>{player['时间']}</td>
                <td class="{score_class}">{player['得分']}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

# ====== 完整的表格显示函数 ======
def display_full_table(players_data):
    """显示完整的球员数据表格"""
    if not players_data:
        st.info("暂无球员数据")
        return
    
    df = pd.DataFrame(players_data)
    if not df.empty:
        # 按得分排序
        df['得分'] = pd.to_numeric(df['得分'], errors='coerce')
        df = df.sort_values('得分', ascending=False)
        df['得分'] = df['得分'].astype(str)
        
        # 显示完整表格（支持水平滚动）
        st.markdown('<div class="full-table-container">', unsafe_allow_html=True)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_order=['球员', '时间', '得分', '投篮', '三分', '罚球', '篮板', '助攻', '失误'],
            column_config={
                "球员": st.column_config.TextColumn(width="medium"),
                "时间": st.column_config.TextColumn(width="small"),
                "得分": st.column_config.NumberColumn(width="small"),
                "投篮": st.column_config.TextColumn(width="small"),
                "三分": st.column_config.TextColumn(width="small"),
                "罚球": st.column_config.TextColumn(width="small"),
                "篮板": st.column_config.NumberColumn(width="small"),
                "助攻": st.column_config.NumberColumn(width="small"),
                "失误": st.column_config.NumberColumn(width="small")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("暂无球员数据")

# ====== 移动端优化的Streamlit界面 ======
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
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.subheader(f"📅 {selected_date.strftime('%Y年%m月%d日')}")

# 加载数据
with st.spinner("加载赛程..."):
    schedule = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule or 'events' not in schedule:
    st.error("无法获取数据，请稍后重试")
    st.stop()

events = schedule['events']
if not events:
    st.info("今日无比赛")
    st.stop()

# 显示比赛列表（移动端优化）
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
    
    # 确定比赛状态和CSS类
    if state == 'in':
        status_badge = "🟢 直播中"
        game_class = "live-game"
    elif state == 'post':
        status_badge = "⚫ 已结束"
        game_class = "finished-game"
    else:
        status_badge = "⏳ 未开始"
        game_class = "upcoming-game"

    # 比赛时间
    try:
        utc_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
        bj_time = utc_time.astimezone(beijing_tz).strftime("%H:%M")
    except:
        bj_time = "时间待定"

    # 比赛卡片
    st.markdown(f'<div class="game-card {game_class} mobile-friendly">', unsafe_allow_html=True)
    
    # 比赛基本信息 - 移动端优化布局
    cols = st.columns([2, 1, 2])
    with cols[0]:
        st.markdown(f'<div class="team-name">{away_name}</div>', unsafe_allow_html=True)
        st.markdown(f'**{away_score}**')
    
    with cols[1]:
        st.markdown("**VS**", help="客队 VS 主队")
        st.markdown(f'<div class="game-time">{bj_time}</div>', unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f'<div class="team-name">{home_name}</div>', unsafe_allow_html=True)
        st.markdown(f'**{home_score}**')
    
    # 状态信息
    st.markdown(f'<span class="status-badge">{status_badge}</span> {desc}', unsafe_allow_html=True)
    
    # 球员数据 - 默认只显示简化版
    if state in ['in', 'post']:
        with st.spinner("加载球员数据..."):
            game_data = fetch_player_stats(event['id'])
            if game_data:
                away_p, home_p = parse_player_stats(game_data)
                
                if away_p or home_p:
                    # 为每个比赛创建唯一的key
                    game_key = f"game_{event['id']}"
                    
                    # 初始化展开状态
                    if game_key not in st.session_state.expanded_games:
                        st.session_state.expanded_games[game_key] = {
                            'away_expanded': False,
                            'home_expanded': False
                        }
                    
                    # 显示球员数据标题
                    st.markdown("---")
                    st.markdown("**球员数据**")
                    
                    # 使用标签页切换主客队
                    tab1, tab2 = st.tabs([f"👤 {away_name}", f"👤 {home_name}"])
                    
                    with tab1:
                        if away_p:
                            # 默认显示简化表格
                            display_simple_table(away_p, away_name)
                            
                            # 展开/收起详细数据按钮
                            col_btn1, col_btn2 = st.columns([1, 1])
                            with col_btn1:
                                if st.button("📊 详细数据", key=f"expand_away_{event['id']}", 
                                          use_container_width=True, 
                                          type="secondary" if not st.session_state.expanded_games[game_key]['away_expanded'] else "primary"):
                                    st.session_state.expanded_games[game_key]['away_expanded'] = not st.session_state.expanded_games[game_key]['away_expanded']
                            
                            with col_btn2:
                                if st.button("📈 得分榜", key=f"score_away_{event['id']}", use_container_width=True):
                                    # 可以添加得分榜功能
                                    pass
                            
                            # 如果展开，显示完整表格
                            if st.session_state.expanded_games[game_key]['away_expanded']:
                                st.markdown("**详细数据**")
                                display_full_table(away_p)
                        else:
                            st.info("暂无球员数据")
                    
                    with tab2:
                        if home_p:
                            # 默认显示简化表格
                            display_simple_table(home_p, home_name)
                            
                            # 展开/收起详细数据按钮
                            col_btn1, col_btn2 = st.columns([1, 1])
                            with col_btn1:
                                if st.button("📊 详细数据", key=f"expand_home_{event['id']}", 
                                          use_container_width=True, 
                                          type="secondary" if not st.session_state.expanded_games[game_key]['home_expanded'] else "primary"):
                                    st.session_state.expanded_games[game_key]['home_expanded'] = not st.session_state.expanded_games[game_key]['home_expanded']
                            
                            with col_btn2:
                                if st.button("📈 得分榜", key=f"score_home_{event['id']}", use_container_width=True):
                                    # 可以添加得分榜功能
                                    pass
                            
                            # 如果展开，显示完整表格
                            if st.session_state.expanded_games[game_key]['home_expanded']:
                                st.markdown("**详细数据**")
                                display_full_table(home_p)
                        else:
                            st.info("暂无球员数据")
                else:
                    st.info("球员数据暂未更新")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 比赛之间的分隔线
    if i < len(events) - 1:
        st.divider()

# 页脚信息
st.divider()
footer_cols = st.columns([3, 1])
with footer_cols[0]:
    st.caption(f"更新时间: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
with footer_cols[1]:
    if st.button("⬆️ 返回顶部", use_container_width=True):
        st.rerun()
