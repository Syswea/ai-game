import streamlit as st
from chat import get_ai_response

# --- 页面配置 ---
st.set_page_config(page_title="海龟汤 AI 调试器", page_icon="🐢")

st.title("🐢 海龟汤 AI 调试后台")
st.markdown("---")

# --- 初始化聊天历史 (Streamlit 会话状态) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 显示历史对话框 (输出框) ---
# 这个区域会自动根据内容增长，展示 AI 和玩家的对话
chat_container = st.container(height=600)
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 玩家输入框 ---
if usr_input := st.chat_input("输入你的推论..."):
    # 1. 在界面显示玩家输入
    with chat_container:
        st.chat_message("user").markdown(usr_input)
    
    # 将输入存入会话状态
    st.session_state.messages.append({"role": "user", "content": usr_input})

    # 2. 调用后端逻辑 (这里你可以连接你的 AI 模型或 API)
    with st.spinner('AI 正在思考中...'):
        try:
            # 占位符：模拟后端返回
            answer = get_ai_response(usr_input)
            
        except Exception as e:
            answer = f"错误：无法连接到后端。{str(e)}"

    # 3. 在界面显示 AI 回复
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(answer)
    
    # 将回复存入会话状态
    st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 侧边栏：调试辅助 ---
with st.sidebar:
    st.header("调试设置")
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()
    st.info("这个页面仅用于快速测试后端逻辑。")