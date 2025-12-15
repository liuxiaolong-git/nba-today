import streamlit as st
import requests
import pytz
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(
    page_title="NBA 今日赛程",
    page_icon="🏀",
    layout="centered"
)

st.title("🏀 NBA 今日赛程")
st.caption("数据来源: balldontlie.io | 美东时间")

# 获取美东时间“今天”
eastern = pytz.timezone('US/Eastern')
today_eastern = datetime.now(eastern).date()
today_str = today_eastern.strftime('%Y-%m-%d')

# 最大可查询日期：今天（不支持未来）
max_date = today_eastern
min_date = max_date - timedelta(days=30)  # 最多查最近30天

# 用户可选日期（默认今天）
selected_date = st.date_input(
    "选择日期（仅限过去30天内）",
    value=today_eastern,
    min_value=min_date,
    max_value=max_date
)

# 转为字符串
selected_date_str = selected_date.strftime('%Y-%m-%d')

# 如果用户选了未来日期（虽然控件限制了，但双重保险）
if selected_date > today_eastern:
    st.warning("⚠️ 无法查询未来的比赛。请选今天或过去的日期。")
    st.stop()

# 带缓存的数据获取函数（缓存60秒）
@st.cache_data(ttl=60)
def fetch_games(date_str):
    try:
        url = "https://www.balldontlie.io/api/v1/games"
        params = {
            'date': date_str,      # ✅ 使用正确的 'date' 参数
            'per_page': 100
        }
        response = requests.get(url, params=params, timeout=10)
        
        # 如果返回 404 或其他错误
        if response.status_code == 404:
            return []  # 视为无数据，而非报错
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    
    except requests.exceptions.Timeout:
        st.error("⏰ 请求超时，请稍后重试。")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 网络请求失败: {e}")
        return []
    except Exception as e:
        st.error(f"💥 未知错误: {e}")
        return []

# 加载比赛数据
games = fetch_games(selected_date_str)

# 显示结果
if not games:
    if selected_date_str == today_str:
        st.info(f"📅 今天（{today_str} 美东时间）暂无 NBA 比赛或数据尚未更新。")
    else:
        st.info(f"📅 {selected_date_str} 没有 NBA 比赛记录。")
else:
    st.success(f"✅ 共找到 {len(games)} 场比赛")
    for game in games:
        home = game['home_team']['full_name']
        visitor = game['visitor_team']['full_name']
        h_score = game['home_team_score']
        v_score = game['visitor_team_score']
        status = game['status']

        # 状态图标
        if "Final" in status:
            icon = "✅"
        elif "Quarter" in status or "Half" in status:
            icon = "🔴"
        else:
            icon = "🕒"

        # 构建比分文本
        if h_score == 0 and v_score == 0 and ("Scheduled" in status or "Not Started" in status):
            score_line = f"{visitor} vs {home}"
        else:
            score_line = f"{visitor} **{v_score} - {h_score}** {home}"

        # 显示比赛卡片
        st.markdown(f"### {icon} {score_line}")
        st.caption(status)
        st.divider()

# 底部说明
st.caption("💡 下拉页面可刷新 | 数据每60秒自动更新")
st.caption("⚠️ 注意：未来比赛无法显示，API 仅提供历史/当日数据")
