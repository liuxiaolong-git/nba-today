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
st.caption("自动加载 | 北京时间显示 | 数据: balldontlie.io")

# === 1. 确定要查询的美东日期（基于北京时间）===
beijing_tz = pytz.timezone('Asia/Shanghai')
eastern_tz = pytz.timezone('US/Eastern')

# 获取当前北京时间
now_beijing = datetime.now(beijing_tz)
today_beijing = now_beijing.date()

# 关键转换：用北京时间中午12点 → 转美东时间 → 取日期
# 这样能稳定对应到正确的比赛日（避免跨午夜问题）
noon_beijing = beijing_tz.localize(
    datetime.combine(today_beijing, datetime.min.time().replace(hour=12))
)
query_eastern_date = noon_beijing.astimezone(eastern_tz).date()
query_eastern_str = query_eastern_date.strftime('%Y-%m-%d')
today_beijing_str = today_beijing.strftime('%Y-%m-%d')

st.info(f"📅 正在加载北京时间 {today_beijing_str} 对应的比赛（美东日期: {query_eastern_str}）")

# === 2. 自动加载数据（带缓存 + 错误处理）===
@st.cache_data(ttl=60)  # 缓存60秒
def fetch_games(date_str):
    try:
        response = requests.get(
            "https://www.balldontlie.io/api/v1/games",
            params={"date": date_str},
            timeout=8
        )
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            return []
    except Exception as e:
        return {"error": str(e)}

# 显示加载状态
with st.spinner("正在获取比赛数据..."):
    result = fetch_games(query_eastern_str)

# === 3. 渲染结果 ===
if isinstance(result, dict) and "error" in result:
    st.error(f"❌ 请求失败: {result['error']}")
elif not result:
    st.warning(f"⚠️ 北京时间 {today_beijing_str} 暂无 NBA 比赛")
    st.info("💡 NBA 赛季通常为每年10月至次年6月，休赛期无比赛。")
else:
    st.success(f"✅ 找到 {len(result)} 场比赛")
    for game in result:
        home = game['home_team']['full_name']
        visitor = game['visitor_team']['full_name']
        hs = game['home_team_score']
        vs = game['visitor_team_score']
        status = game['status']

        # 状态图标
        if "Final" in status:
            icon = "✅"
        elif "Quarter" in status or "Half" in status:
            icon = "🔴"
        else:
            icon = "🕒"

        # 比分文本
        if hs == 0 and vs == 0 and ("Scheduled" in status or "Not Started" in status):
            score_line = f"{visitor} vs {home}"
        else:
            score_line = f"{visitor} **{vs} - {hs}** {home}"

        st.markdown(f"### {icon} {score_line}")
        st.caption(status)
        st.divider()

# 底部说明
st.caption("数据每60秒自动刷新 | 下拉页面可手动更新")
