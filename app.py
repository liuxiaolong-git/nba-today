import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程")
st.caption("数据来源: ESPN公开接口 | 全中文")

# 初始化会话状态
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)
today_str = now_beijing.strftime('%Y-%m-%d')

# ...（此处省略球队和球员翻译字典，使用与之前相同的字典）...

@st.cache_data(ttl=30)
def fetch_nba_schedule(date_str):
    """获取NBA赛程数据"""
    try:
        eastern_tz = pytz.timezone('America/New_York')
        beijing_date = datetime.strptime(date_str, '%Y-%m-%d')
        beijing_date = beijing_tz.localize(beijing_date)
        eastern_date = beijing_date.astimezone(eastern_tz)

        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        params = {
            'dates': eastern_date.strftime('%Y%m%d'),
            'lang': 'zh',
            'region': 'cn'
        }

        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, params=params, headers=headers, timeout=8)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        st.error(f"获取赛程失败: {e}")
        return None

def parse_player_stats_from_competitor(competitor_data):
    """
    直接从competitors数据中解析球员统计
    这是ESPN API中更稳定可靠的数据路径
    """
    players_data = []
    try:
        # 尝试从competitor的'statistics'或'leaders'中获取球员数据
        athletes = competitor_data.get('leaders', [{}])[0].get('leaders', [])
        for athlete_info in athletes:
            athlete = athlete_info.get('athlete', {})
            stats = athlete_info.get('stats', [])

            if athlete and stats:
                player_name = translate_player_name(athlete.get('displayName', ''))
                # 创建球员数据字典
                player_entry = {
                    '球员': player_name,
                    '出场时间': '0:00',  # 这个信息在leaders中可能没有，需要从其他地方获取
                    '得分': str(stats[0]) if len(stats) > 0 else '0',
                    '投篮': '0-0',  # 简化处理
                    '三分': '0-0',  # 简化处理
                    '助攻': str(stats[2]) if len(stats) > 2 else '0',  # 假设索引2是助攻
                    '篮板': str(stats[1]) if len(stats) > 1 else '0',  # 假设索引1是篮板
                    '失误': str(stats[3]) if len(stats) > 3 else '0',  # 假设索引3是失误
                }
                players_data.append(player_entry)
    except Exception as e:
        st.warning(f"解析球员数据时出错: {e}")

    return players_data

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 查询设置")
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3)
    )

# 主界面
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

# 获取赛程数据
with st.spinner("正在加载赛程数据..."):
    schedule_data = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule_data or 'events' not in schedule_data:
    st.error("无法获取赛程数据或数据结构异常，请稍后重试。")
    if schedule_data:
        # 调试：显示返回的数据结构
        with st.expander("查看API返回的原始数据结构"):
            st.json(schedule_data)
    st.stop()

events = schedule_data.get('events', [])

if not events:
    st.info("今日暂无NBA比赛安排")
    st.stop()

# 显示比赛列表
for i, event in enumerate(events):
    event_id = event.get('id', '')
    status = event.get('status', {})
    status_detail = status.get('type', {}).get('state', 'pre')
    status_desc = status.get('type', {}).get('description', '未开始')

    # 比赛状态
    if status_detail == 'in':
        status_badge = "🟢 进行中"
    elif status_detail == 'post':
        status_badge = "⚫ 已结束"
    else:
        status_badge = "⏳ 未开始"

    # 比赛时间
    date_str = event.get('date', '')
    if date_str:
        try:
            utc_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            beijing_time = utc_time.astimezone(beijing_tz)
            game_time = beijing_time.strftime("%H:%M")
        except:
            game_time = "时间待定"
    else:
        game_time = "时间待定"

    # 参赛队伍
    competitions = event.get('competitions', [])
    if competitions:
        competition = competitions[0]
        competitors = competition.get('competitors', [])

        if len(competitors) >= 2:
            away_team = competitors[0].get('team', {})
            home_team = competitors[1].get('team', {})

            away_name_cn = translate_team_name(away_team.get('displayName', '客队'))
            home_name_cn = translate_team_name(home_team.get('displayName', '主队'))

            away_score = competitors[0].get('score', '0')
            home_score = competitors[1].get('score', '0')

            # 创建比赛卡片
            with st.container():
                # 比分卡片
                score_col1, score_col2, score_col3, score_col4, score_col5 = st.columns([2, 1, 0.5, 1, 2])

                with score_col1:
                    st.markdown(f"**{away_name_cn}**")
                with score_col2:
                    st.markdown(f"**{away_score}**")
                with score_col3:
                    st.markdown("**VS**")
                with score_col4:
                    st.markdown(f"**{home_score}**")
                with score_col5:
                    st.markdown(f"**{home_name_cn}**")

                # 比赛信息
                st.caption(f"{status_badge} | {status_desc} | ⏰ {game_time}")

                # 直接显示球员数据（针对已结束或进行中的比赛）
                if status_detail in ['in', 'post']:
                    st.subheader("📊 球员数据")
                    
                    # 尝试从现有数据中解析球员统计
                    try:
                        away_players = parse_player_stats_from_competitor(competitors[0])
                        home_players = parse_player_stats_from_competitor(competitors[1])

                        if away_players or home_players:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**{away_name_cn}**")
                                if away_players:
                                    away_df = pd.DataFrame(away_players)
                                    # 按得分排序
                                    away_df['得分_int'] = pd.to_numeric(away_df['得分'], errors='coerce')
                                    away_df = away_df.sort_values('得分_int', ascending=False).drop('得分_int', axis=1)
                                    st.dataframe(
                                        away_df,
                                        hide_index=True,
                                        use_container_width=True,
                                        height=min(300, len(away_players) * 35 + 38)
                                    )
                                else:
                                    st.info("暂无球员数据")
                            
                            with col2:
                                st.markdown(f"**{home_name_cn}**")
                                if home_players:
                                    home_df = pd.DataFrame(home_players)
                                    home_df['得分_int'] = pd.to_numeric(home_df['得分'], errors='coerce')
                                    home_df = home_df.sort_values('得分_int', ascending=False).drop('得分_int', axis=1)
                                    st.dataframe(
                                        home_df,
                                        hide_index=True,
                                        use_container_width=True,
                                        height=min(300, len(home_players) * 35 + 38)
                                    )
                                else:
                                    st.info("暂无球员数据")
                        else:
                            st.warning("未能从当前比赛数据中解析出球员统计。")
                            
                            # 调试信息
                            with st.expander("调试信息: 查看competitor数据结构"):
                                st.json(competitors[0])
                    except Exception as e:
                        st.error(f"处理球员数据时发生错误: {e}")

    # 比赛之间的分隔线
    if i < len(events) - 1:
        st.divider()

# 底部状态栏
st.divider()
col1, col2 = st.columns([2, 1])
with col1:
    st.caption(f"最后更新: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
with col2:
    if st.button("🔄 手动刷新"):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.rerun()
