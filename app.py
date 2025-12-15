import streamlit as st
import requests
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA 今日赛程", page_icon="🏀", layout="centered")
st.title("🏀 NBA 今日赛程")
st.caption("数据来源: balldontlie.io | 美东时间")

eastern = pytz.timezone('US/Eastern')
today_eastern = datetime.now(eastern).date()
selected_date = st.date_input(
    "选择日期（仅限过去30天内）",
    value=today_eastern,
    min_value=today_eastern - timedelta(days=30),
    max_value=today_eastern
)

if selected_date > today_eastern:
    st.warning("⚠️ 无法查询未来的比赛。")
    st.stop()

# >>> 关键：只在用户点击“加载”后才请求数据 <<<
if st.button("🚀 加载比赛数据"):
    with st.spinner(f"正在获取 {selected_date} 的比赛数据..."):
        try:
            url = "https://www.balldontlie.io/api/v1/games"
            response = requests.get(url, params={'date': selected_date.strftime('%Y-%m-%d')}, timeout=8)
            if response.status_code == 200:
                games = response.json().get('data', [])
                if not games:
                    st.info("📅 当天无比赛记录。")
                else:
                    for g in games:
                        home, visitor = g['home_team']['full_name'], g['visitor_team']['full_name']
                        hs, vs = g['home_team_score'], g['visitor_team_score']
                        status = g['status']
                        icon = "✅" if "Final" in status else "🔴" if ("Quarter" in status or "Half" in status) else "🕒"
                        score = f"{visitor} vs {home}" if (hs == 0 and vs == 0 and "Scheduled" in status) else f"{visitor} **{vs} - {hs}** {home}"
                        st.markdown(f"### {icon} {score}")
                        st.caption(status)
                        st.divider()
            else:
                st.error("❌ 未找到比赛数据（可能是未来日期或API限制）")
        except Exception as e:
            st.error(f"💥 错误: {str(e)}")
else:
    st.info("👉 点击下方按钮加载比赛数据")
