import streamlit as st
from chatbot_engine import chatbot
from analytics import get_status_summary, get_monthly_trend
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Policy AI Assistant", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat Assistant", "Dashboard"])

# ================= CHAT =================
if page == "Chat Assistant":

    st.title("🤖 Policy AI Assistant")

    if "history" not in st.session_state:
        st.session_state.history = []

    question = st.text_input("Ask about policy cases")

    if st.button("Send") and question:
        reply = chatbot(question)
        st.session_state.history.append(("You", question))
        st.session_state.history.append(("Bot", reply))
        # clear box
        st.session_state.user_input = ""

    for sender, msg in st.session_state.history:
        st.write(f"**{sender}:** {msg}")

# ================= DASHBOARD =================
elif page == "Dashboard":

    st.title("📊 Operations Dashboard")

    status_data = get_status_summary()
    trend_data = get_monthly_trend()

    df_status = pd.DataFrame(status_data)
    df_trend = pd.DataFrame(trend_data)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Status Distribution")
        #fig1 = px.pie(df_status, names="status", values="total")
        fig1 = px.pie(df_status, names="request_status", values="total")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Monthly Trend")
        fig2 = px.line(df_trend, x="month", y="total", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Status Data")
    st.dataframe(df_status)