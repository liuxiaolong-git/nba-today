import streamlit as st
import requests
import pytz
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="centered")
st.title("🏀 NBA今日赛程查询")
st.caption("数据来源: 公开NBA接口 | 完全免费 | 自动更新")

# 获取北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)
today_str = now_beijing.strftime('%Y-%m-%d')
st.write(f"**查询日期（北京时间）:** {today_str}")

# 免费公开API - 不需要API Key
@st.cache_data(ttl=600)  # 缓存10分钟
def fetch_nba_games(date_str):
    """
    从公开接口获取NBA赛程数据
    参数date_str格式: YYYY-MM-DD (北京时间)
    """
    try:
        # 方案1: 使用一个稳定的公开NBA数据接口
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        
        # 将北京时间转换为美东时间进行请求（因为NBA赛程通常按美东时间发布）
        eastern_tz = pytz.timezone('America/New_York')
        beijing_date = datetime.strptime(date_str, '%Y-%m-%d')
        beijing_date = beijing_tz.localize(beijing_date)
        eastern_date = beijing_date.astimezone(eastern_tz)
        
        params = {
            'dates': eastern_date.strftime('%Y%m%d'),
            'lang': 'zh',
            'region': 'cn'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        with st.spinner(f"正在获取 {date_str} 的赛程数据..."):
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
        return data
        
    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败: {e}")
        return None
    except Exception as e:
        st.error(f"数据处理失败: {e}")
        return None

# 获取数据
data = fetch_nba_games(today_str)

if not data:
    # 尝试备用方案：如果今天没比赛，尝试获取最近有比赛的日期
    st.info("正在尝试查找最近的比赛...")
    for i in range(1, 4):  # 检查前后3天
        # 检查过去
        past_date = (now_beijing - timedelta(days=i)).strftime('%Y-%m-%d')
        past_data = fetch_nba_games(past_date)
        if past_data and past_data.get('events'):
            data = past_data
            st.info(f"今天没有比赛，显示 {past_date} 的比赛")
            break
            
        # 检查未来
        future_date = (now_beijing + timedelta(days=i)).strftime('%Y-%m-%d')
        future_data = fetch_nba_games(future_date)
        if future_data and future_data.get('events'):
            data = future_data
            st.info(f"今天没有比赛，显示 {future_date} 的比赛")
            break
    
    if not data:
        st.warning("暂时无法获取赛程数据，请稍后重试")
        st.stop()

# 解析并显示比赛数据
events = data.get('events', [])
if not events:
    st.info("今日暂无NBA比赛安排")
    st.stop()

st.success(f"找到 {len(events)} 场比赛")

# 显示每场比赛的详细信息
for event in events:
    # 比赛基本信息
    name = event.get('name', '未知比赛')
    short_name = event.get('shortName', name)
    
    # 比赛状态
    status = event.get('status', {})
    status_type = status.get('type', {})
    status_desc = status.get('description', '未开始')
    
    # 确定状态颜色
    if 'final' in status_desc.lower() or '结束' in status_desc:
        status_color = "gray"
        status_text = "比赛结束"
    elif 'quarter' in status_desc.lower() or '节' in status_desc:
        status_color = "orange"
        status_text = status_desc
    else:
        status_color = "green"
        status_text = "未开始"
    
    # 比赛时间（转换为北京时间）
    date_str = event.get('date', '')
    if date_str:
        try:
            # 原始时间是UTC，转换为北京时间
            utc_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            beijing_time = utc_time.astimezone(beijing_tz)
            game_time = beijing_time.strftime("%Y-%m-%d %H:%M")
        except:
            game_time = "时间待定"
    else:
        game_time = "时间待定"
    
    # 参赛队伍
    competitions = event.get('competitions', [])
    if competitions:
        competitors = competitions[0].get('competitors', [])
        if len(competitors) >= 2:
            away_team = competitors[0].get('team', {}).get('displayName', '客队')
            home_team = competitors[1].get('team', {}).get('displayName', '主队')
            
            # 比分信息
            away_score = competitors[0].get('score', '0')
            home_score = competitors[1].get('score', '0')
            
            # 显示比赛卡片
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.markdown(f"**{away_team}**")
                if status_text != "未开始":
                    st.markdown(f"### {away_score}")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**VS**")
                st.markdown(f"<span style='color:{status_color}; font-size:0.8em'>{status_text}</span>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"**{home_team}**")
                if status_text != "未开始":
                    st.markdown(f"### {home_score}")
            
            # 比赛时间和详情
            with st.expander("比赛详情"):
                st.write(f"**比赛时间（北京时间）:** {game_time}")
                st.write(f"**比赛状态:** {status_desc}")
                
                # 如果有直播链接
                links = event.get('links', [])
                for link in links[:2]:  # 只显示前2个链接
                    if 'href' in link:
                        st.markdown(f"[观看直播或详情]({link['href']})")
    
    st.divider()

# 添加日期选择功能
st.sidebar.header("查询其他日期")
selected_date = st.sidebar.date_input("选择日期", value=now_beijing.date())

if selected_date.strftime('%Y-%m-%d') != today_str:
    st.sidebar.write(f"查询 {selected_date.strftime('%Y-%m-%d')} 的比赛")
    if st.sidebar.button("查询"):
        new_data = fetch_nba_games(selected_date.strftime('%Y-%m-%d'))
        if new_data:
            st.experimental_rerun()

# 显示数据更新时间
st.caption(f"数据更新时间: {datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')}")
