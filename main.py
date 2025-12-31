import streamlit as st
from chat import get_ai_response

# --- 页面配置 ---
st.set_page_config(page_title="海龟汤 AI 调试器", page_icon="🐢", layout="wide")

st.title("🐢 海龟汤 AI 级联推理调试器")

# --- 初始化会话状态 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "open_context" not in st.session_state:
    st.session_state.open_context = "暂无汤面，请在侧边栏设置"
if "main_context" not in st.session_state:
    st.session_state.main_context = "暂无汤底"

# --- 侧边栏 & 弹窗配置 ---
with st.sidebar:
    st.header("游戏配置")
    
    # 使用 popover 组件实现弹窗输入
    with st.popover("📝 设置汤面与汤底"):
        st.write("请在此输入本局游戏的设定：")
        new_open = st.text_area("汤面 (玩家可见):", value=st.session_state.open_context)
        new_main = st.text_area("汤底 (AI 判准):", value=st.session_state.main_context)
        
        if st.button("确认更新设定"):
            st.session_state.open_context = new_open
            st.session_state.main_context = new_main
            st.success("设定已更新！")
            st.rerun()

    if st.button("🧹 清空所有对话"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.info(f"**当前汤面预览：**\n{st.session_state.open_context[:50]}")

# --- 对话展示区 ---
chat_container = st.container(height=500)

with chat_container:
    # 始终在最上方展示当前汤面
    st.info(f"📜 **汤面：** {st.session_state.open_context}")
    
    # 渲染历史消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 玩家输入处理 ---
if usr_input := st.chat_input("输入你的判断句..."):
    # 1. 展示用户输入
    with chat_container:
        st.chat_message("user").markdown(usr_input)
    st.session_state.messages.append({"role": "user", "content": usr_input})

    # 2. 调用后端推理
    with st.spinner('AI 正在进行级联推理 (分析->正反证->决策)...'):
        try:
            # 【关键修改】：将前端输入的背景传入后端
            answer = get_ai_response(
                usr_input, 
                st.session_state.open_context, 
                st.session_state.main_context
            )
        except Exception as e:
            answer = f"❌ 后端调用失败: {str(e)}"

    # 3. 展示 AI 回复
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})